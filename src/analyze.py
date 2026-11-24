"""Remote-only orchestration for the PV contributing-drainage estimate."""
from hydro import *
from render import render

def main():
    reference = ROOT / "data/reference/pv_subbasin.geojson"
    reference_meta = json.loads((ROOT / "data/reference/boundary_provenance.json").read_text())
    assert hashlib.sha256(reference.read_bytes()).hexdigest() == reference_meta["sha256"]
    pv_ll = geometry(json.loads(reference.read_bytes()))
    pv = transform(TO_M, pv_ll)
    assert 74 < pv.area/M2_PER_SQMI < 77, "Wrong DWR basin or CRS"
    bounds = pv_ll.bounds
    # Margin supplies independent neighboring-node checks and nearby creek names.
    bbox = (bounds[0]-.07, bounds[1]-.07, bounds[2]+.07, bounds[3]+.07)
    network = collection("nhd_network", "nhdflowline_network", bbox, PROPERTIES)
    lines = {}
    for feature in network["features"]:
        prop = feature["properties"]
        assert prop["flowdir"] == "With Digitized", "Unknown flow direction needs explicit review"
        comid = int(prop["comid"])
        assert comid not in lines
        lines[comid] = {"properties": prop,
                        "line": normalize_line(transform(TO_M, shape(feature["geometry"])))}
    qa = topology_qa(lines)
    all_events = []
    entry_sets = {}
    for inset in (0, 100, 250):
        target = pv.buffer(-inset)
        assert not target.is_empty
        events = crossings(lines, target, inset)
        all_events.extend(events)
        entry_sets[inset] = {event["comid"] for event in events if event["event"] == "enter"}
    event_frame = pd.DataFrame(all_events)
    event_frame.to_csv(OUT / "all_boundary_crossing_events.csv", index=False)
    assert not (event_frame.event == "endpoint_uncertain").any(), "Ambiguous endpoint crossings need review"
    requested_ids = set.union(*entry_sets.values())
    assert requested_ids
    print(f"Fetching {len(requested_ids)} upstream basins, local catchments and navigation traces", flush=True)
    sources = {}
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        for comid, source in pool.map(inlet_sources, sorted(requested_ids)):
            sources[comid] = source
            print("Verified drainage source", comid, flush=True)
    assert set(sources) == requested_ids, "Missing inlet basin cannot be silently dropped"
    masks = {}
    sensitivity = []
    for inset, identifiers in entry_sets.items():
        upper = make_valid(union_all([sources[c]["basin"] for c in identifiers]).difference(pv))
        lower = make_valid(union_all([sources[c]["basin"].difference(sources[c]["local"])
                                     for c in identifiers]).difference(pv))
        assert lower.difference(upper).area < 1, "Lower area exceeds upper"
        assert upper.intersection(pv).area < 1 and lower.intersection(pv).area < 1
        masks[inset] = lower, upper
        sensitivity.append({"boundary_inset_m": inset, "n_entry_reaches": len(identifiers),
                            "external_lower_sqmi": lower.area/M2_PER_SQMI,
                            "external_upper_sqmi": upper.area/M2_PER_SQMI,
                            "removed_comids_vs_original": ",".join(map(str, sorted(entry_sets[0]-identifiers))),
                            "added_comids_vs_original": ",".join(map(str, sorted(identifiers-entry_sets[0])))})
    pd.DataFrame(sensitivity).to_csv(OUT / "boundary_geometry_sensitivity.csv", index=False)
    lower, upper = masks[0]
    selected = sorted(entry_sets[0])
    core = pv.buffer(-100)
    inside_reaches = {comid for comid, row in lines.items() if row["line"].intersection(core).length > 20}
    inlet_rows = []
    for comid in selected:
        prop, source = lines[comid]["properties"], sources[comid]
        events = [e for e in all_events if e["inset_m"] == 0 and e["comid"] == comid and e["event"] == "enter"]
        first_distance = min(e["distance_along_m"] for e in events)
        own_before_inside = substring(lines[comid]["line"], 0, max(0, first_distance-0.001)).intersection(core).length > 0.1
        upstream_inside = bool((source["upstream_ids"]-{comid}) & inside_reaches)
        upstream_names = sorted({str(lines[c]["properties"].get("gnis_name", "")).strip()
                                 for c in source["upstream_ids"] & set(lines)
                                 if str(lines[c]["properties"].get("gnis_name", "")).strip()})
        name = str(prop.get("gnis_name", "")).strip()
        qa_flow, qc_flow, qe_flow = [finite_flow(prop.get(field)) for field in ("qa_ma", "qc_ma", "qe_ma")]
        inlet_rows.append({"comid": comid, "reach_name": name or f"Unnamed reach {comid}",
                           "upstream_named_streams_in_local_window": "; ".join(upstream_names),
                           "entry_event_count": len(events),
                           "reentry_or_upstream_PV_contact_flag": upstream_inside or own_before_inside or len(events) > 1,
                           "has_multiple_entry_events": len(events) > 1,
                           "upstream_network_reaches": len(source["upstream_ids"]),
                           "external_lower_sqmi": source["basin"].difference(source["local"]).difference(pv).area/M2_PER_SQMI,
                           "external_upper_sqmi": source["basin"].difference(pv).area/M2_PER_SQMI,
                           "local_catchment_in_basin_fraction": source["local_in_basin_fraction"],
                           "local_catchment_method": source["local_catchment_method"],
                           "qa_runoff_cfs_1971_2000_outlet": qa_flow,
                           "qc_reference_cfs_1971_2000_outlet": qc_flow,
                           "qe_gage_adjusted_cfs_1971_2000_outlet": qe_flow,
                           "qa_runoff_afyr_outlet_proxy": qa_flow*CFS_TO_AFYR if qa_flow is not None else None,
                           "qe_gage_adjusted_afyr_outlet_proxy": qe_flow*CFS_TO_AFYR if qe_flow is not None else None,
                           "divergence": prop.get("divergence"), "return_divergence": prop.get("rtndiv"),
                           "downstream_drainage_count": prop.get("dndraincou"), "feature_type": prop.get("ftype")})
    inlets = pd.DataFrame(inlet_rows).sort_values("qa_runoff_cfs_1971_2000_outlet", ascending=False)
    inlets.to_csv(OUT / "inlet_reach_runoff_proxies.csv", index=False)
    monthly_rows = []
    for comid in selected:
        prop = lines[comid]["properties"]
        for month in range(1, 13):
            monthly_rows.append({"comid": comid, "month": month,
                                 "period": "1971-2000 mean monthly",
                                 **{f"{prefix}_cfs_reach_outlet": finite_flow(prop.get(f"{prefix}_{month:02}"))
                                    for prefix in ("qa", "qc", "qe")}})
    pd.DataFrame(monthly_rows).to_csv(OUT / "inlet_monthly_runoff_proxies.csv", index=False)
    (OUT / "upstream_comids_by_inlet.json").write_text(json.dumps(
        {str(c): sorted(sources[c]["upstream_ids"]) for c in selected}, indent=2))
    save_geojson(OUT / "contributing_area_bracket.geojson", [
        geo_feature(lower, {"area": "conservative_upstream_catchments", "square_miles": lower.area/M2_PER_SQMI}),
        geo_feature(upper, {"area": "including_whole_entry_catchments", "square_miles": upper.area/M2_PER_SQMI})])
    save_geojson(OUT / "pv_subbasin.geojson", [geo_feature(pv, {"name": "Pleasant Valley 5-022.10"})])
    event_features = [geo_feature(Point(e["x"], e["y"]), {
        "comid": e["comid"], "event": e["event"],
        "name": str(lines[e["comid"]]["properties"].get("gnis_name", "")).strip()})
        for e in all_events if e["inset_m"] == 0 and e["x"] is not None]
    save_geojson(OUT / "boundary_events.geojson", event_features)
    upper_ll = transform(TO_LL, upper)
    bx = upper_ll.bounds
    huc_payload = collection("huc12_2025", "wbd12_20250107",
                             (bx[0]-.01, bx[1]-.01, bx[2]+.01, bx[3]+.01))
    huc_features, huc_rows, clips = [], [], []
    for feature in huc_payload["features"]:
        geom = transform(TO_M, make_valid(shape(feature["geometry"])))
        clip = geom.intersection(upper)
        if clip.area < 1000:
            continue
        prop = feature["properties"]
        huc_id = str(prop.get("huc12", feature.get("id", "")))
        assert huc_id and len(huc_id) == 12, "Missing HUC12 identifier"
        row = {"huc12": huc_id, "name": prop.get("name", huc_id),
               "contributing_lower_sqmi": geom.intersection(lower).area/M2_PER_SQMI,
               "contributing_upper_sqmi": clip.area/M2_PER_SQMI,
               "full_huc12_sqmi": geom.area/M2_PER_SQMI,
               "fraction_of_huc12_in_upper_mask": clip.area/geom.area,
               "small_boundary_intersection_under_0_1_sqmi": clip.area/M2_PER_SQMI < 0.1}
        huc_rows.append(row)
        huc_features.append(geo_feature(clip, row))
        clips.append(clip)
    hucs = pd.DataFrame(huc_rows).sort_values("contributing_upper_sqmi", ascending=False)
    assert hucs.huc12.is_unique
    hucs.to_csv(OUT / "contributing_huc12_reporting_units.csv", index=False)
    save_geojson(OUT / "contributing_huc12.geojson", huc_features)
    huc_union = union_all(clips)
    uncovered = upper.difference(huc_union).area
    huc_overlap = sum(c.area for c in clips)-huc_union.area
    assert uncovered/upper.area < 0.001 and abs(huc_overlap)/upper.area < 0.001
    # Public legacy source: boundary-flow polygons are compared, never presumed upstream.
    meta = get_json("cvhm2_smallwatersheds_metadata.json",
                    "https://www.sciencebase.gov/catalog/item/62201161d34ee0c6b38a870d", {"format": "json"})
    facets = [facet for facet in meta.get("facets", []) if facet.get("name") == "CVHM2_smallwatersheds"]
    assert len(facets) == 1, "Identify the exact published shapefile facet"
    components = facets[0]["files"]
    names = {component["name"] for component in components}
    assert {"CVHM2_smallwatersheds.shp", "CVHM2_smallwatersheds.shx",
            "CVHM2_smallwatersheds.dbf", "CVHM2_smallwatersheds.prj"} <= names
    for component in components:
        assert Path(component["name"]).name == component["name"], "Unsafe component path"
        original = download(component["name"], component["url"])
        assert original.stat().st_size == int(component["size"])
        assert hashlib.md5(original.read_bytes()).hexdigest() == component["checksum"]["value"]
    legacy = gpd.read_file(RAW / "CVHM2_smallwatersheds.shp").to_crs(3310)
    assert len(legacy) == 65 and legacy.ID.nunique() == 56, "Wrong source layer or changed publisher dataset"
    legacy_rows, legacy_features = [], []
    for index, row in legacy.iterrows():
        if row.geometry.distance(pv) > 30000:
            continue
        outside = row.geometry.difference(pv)
        if outside.area <= 0:
            continue
        record = {"feature_index": int(index), "source_id": int(row["ID"]),
                  "source_name": str(row["HUCName"]), "distance_to_PV_km": row.geometry.distance(pv)/1000,
                  "legacy_selected_by_1_5km": bool(row.geometry.distance(pv) <= 1500),
                  "external_polygon_sqmi": outside.area/M2_PER_SQMI,
                  "contributing_lower_sqmi": outside.intersection(lower).area/M2_PER_SQMI,
                  "contributing_upper_sqmi": outside.intersection(upper).area/M2_PER_SQMI,
                  "percent_in_upper_contributing_mask": 100*outside.intersection(upper).area/outside.area}
        legacy_rows.append(record)
        legacy_features.append(geo_feature(row.geometry, record))
    legacy_frame = pd.DataFrame(legacy_rows)
    legacy_frame.to_csv(OUT / "legacy_small_watershed_connectivity_comparison.csv", index=False)
    save_geojson(OUT / "legacy_small_watersheds_near_PV.geojson", legacy_features)
    raw_sum = sum(sources[c]["basin"].difference(pv).area for c in selected)
    orientation = pd.read_csv(OUT / "topology_orientation_checks.csv")
    relevant_pairs = orientation.loc[orientation.upstream_comid.isin(selected) | orientation.downstream_comid.isin(selected)]
    assert not ((relevant_pairs.correct_endpoint_gap_m > 100) & (relevant_pairs.reversed_endpoint_gap_m <= 100)).any(), "Entry orientation reversed against adjacent nodes"
    checked_entry_ids = set(relevant_pairs.upstream_comid) | set(relevant_pairs.downstream_comid)
    qa.update({"boundary_coincident_events": int((event_frame.event == "boundary_coincident").sum()),
               "entry_reaches_without_adjacent_orientation_evidence": sorted(set(selected)-checked_entry_ids),
               "catchmentless_reaches": {str(c):s["local_catchment_method"] for c,s in sources.items()
                                         if s["local_catchment_method"] != "native_mapped_local_catchment"},
               "status": "passed_automated_checks_preliminary_estimate",
               "PV_area_sqmi": pv.area/M2_PER_SQMI, "local_network_reaches": len(lines),
               "entry_reaches_original_boundary": len(selected),
               "entry_events_original_boundary": sum(e["inset_m"] == 0 and e["event"] == "enter" for e in all_events),
               "all_requested_upstream_sources_present": set(sources) == requested_ids,
               "external_lower_sqmi": lower.area/M2_PER_SQMI,
               "external_upper_sqmi": upper.area/M2_PER_SQMI,
               "overlapping_basin_area_removed_sqmi": (raw_sum-upper.area)/M2_PER_SQMI,
               "huc12_reporting_units": len(hucs), "huc12_uncovered_sqmi": uncovered/M2_PER_SQMI,
               "huc12_overlap_sqmi": huc_overlap/M2_PER_SQMI,
               "minimum_local_catchment_in_basin_fraction": min(s["local_in_basin_fraction"] for s in sources.values()),
               "flux_total_intentionally_not_computed": True,
               "software": {"python": platform.python_version(), "geopandas": gpd.__version__,
                            "pandas": pd.__version__, "numpy": np.__version__},
               "completed_utc": utc()})
    (OUT / "qa_checks.json").write_text(json.dumps(qa, indent=2))
    source_unique = {source["file"]: source for source in SOURCES}
    (ROOT / "data/source_manifest.json").write_text(json.dumps(
        {"pinned_boundary": reference_meta, "public_api_responses": list(source_unique.values())}, indent=2))
    render(pv, lower, upper, lines, selected, inlets, hucs, legacy_frame, sensitivity, qa)
    print(json.dumps(qa, indent=2), flush=True)



if __name__ == "__main__":
    main()
