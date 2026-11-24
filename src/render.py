"""Publish the report, interactive map and source-linked results."""
from hydro import *

def markdown_table(frame):
    columns = list(frame.columns)
    rows = ["| "+" | ".join(columns)+" |", "| "+" | ".join("---" for _ in columns)+" |"]
    for values in frame.itertuples(index=False, name=None):
        rows.append("| "+" | ".join("" if pd.isna(v) else f"{v:.2f}" if isinstance(v, (float, np.floating)) else str(v).replace("|", "/") for v in values)+" |")
    return "\n".join(rows)


def render(pv, lower, upper, lines, selected, inlets, hucs, legacy, sensitivity, qa):
    fig, ax = plt.subplots(figsize=(11, 9))
    gpd.GeoSeries([upper], crs=3310).plot(ax=ax, facecolor="#b7d5ea", edgecolor="#417ca7", linewidth=.6)
    gpd.GeoSeries([lower], crs=3310).plot(ax=ax, facecolor="#7ab69d", edgecolor="none", alpha=.8)
    relevant = [row["line"] for row in lines.values() if row["line"].intersects(upper.union(pv))]
    gpd.GeoSeries(relevant, crs=3310).plot(ax=ax, color="#356688", linewidth=.5)
    gpd.GeoSeries([pv], crs=3310).plot(ax=ax, facecolor="#f6c77c", edgecolor="#ab5e0a", linewidth=1.7)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("Potential external runoff-contributing drainage to Pleasant Valley\n"
                 "Green: excludes boundary-reach catchments; blue: includes them; orange: PV\n"
                 "Network estimate, not measured inflow or recharge", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "contributing_drainage.png", dpi=160)
    plt.close(fig)
    first = inlets.loc[~inlets.reentry_or_upstream_PV_contact_flag].copy()
    display = first[["comid", "reach_name", "upstream_named_streams_in_local_window",
                     "external_lower_sqmi", "external_upper_sqmi",
                     "qa_runoff_cfs_1971_2000_outlet", "qe_gage_adjusted_cfs_1971_2000_outlet"]]
    selected_legacy = legacy.loc[legacy.legacy_selected_by_1_5km, [
        "source_id", "feature_index", "percent_in_upper_contributing_mask",
        "contributing_lower_sqmi", "contributing_upper_sqmi"]]
    report = f"""# Pleasant Valley potential runoff-contributing drainage

Preliminary network estimate completed {qa['completed_utc']}. Source snapshots and all derivation code are included in this public repository. Computation occurred on a GitHub-hosted runner.

## Main estimate

**External contributing land: {qa['external_lower_sqmi']:.1f}â€“{qa['external_upper_sqmi']:.1f} square miles**, before any allowance for losses, diversions or transmission failure. PV itself ({qa['PV_area_sqmi']:.2f} square miles) is excluded.

The lower mask includes whole catchments upstream of each boundary-crossing reach but excludes that reach's entire local catchment. The upper mask includes the whole local catchment. This bracket describes uncertainty in the exact stream-entry position within a mapped reach. It is **not** a statistical confidence interval or a bound on actual delivered runoff.

The directed network identifies {qa['entry_reaches_original_boundary']} entry reaches and {qa['entry_events_original_boundary']} entry events. Their upstream basins overlap: spatial union removes {qa['overlapping_basin_area_removed_sqmi']:.1f} square miles that would otherwise be counted repeatedly. Reentries remain in the area union because they may receive additional exterior drainage.

## Runoff-based inlet evidence

EROM qa is conservatively accumulated flow from modeled runoff. qc is a reference-gage-adjusted natural-flow proxy; qe is a gage-adjusted proxy. These are **1971â€“2000 mean flows in cubic feet per second at the downstream end of each NHDPlus reach**, not observations or present-year flux at the exact PV boundary.

The following table filters reaches flagged as having an upstream PV interior contact. This helps interpretation, but is not a complete independent set of watershed fluxes. Named upstream streams are restricted to the local query window. **Do not sum these rows:** divergent branches, nested drainage and boundary reentries can share contributing areas. Full entry and exit details are in the CSVs.

{markdown_table(display)}

## Small-watershed reporting units

HUC12 polygons partition the contributing mask for reporting and climate-data extraction. They are not automatically separate inlet basins. The model identifies portions of {len(hucs)} HUC12 units. Coverage and overlap reconcile in qa_checks.json.

{markdown_table(hucs[['huc12','name','contributing_lower_sqmi','contributing_upper_sqmi']])}

## Comparison with the legacy nearby CVHM2 polygons

The earlier rule selected any polygon within 1.5 km of PV. This table checks those same source polygons against the network-derived mask; an ID may occur on multiple polygons. The percentages refer to the part outside PV.

{markdown_table(selected_legacy)}

A high intersection percentage indicates mapped upstream connectivity, not a measured delivery fraction. A low percentage demonstrates why proximity alone cannot identify PV contributors. The CVHM2 layer represents foothill boundary-flow areas for the regional model and is not complete drainage coverage for PV.

## Boundary geometry sensitivity

Inward offsets test alignment differences between the groundwater-basin outline and medium-resolution stream geometry. The original boundary remains the main estimate. Insetting can remove genuine boundary-following channels; it does not establish which boundary interpretation is correct.

{markdown_table(pd.DataFrame(sensitivity)[['boundary_inset_m','n_entry_reaches','external_lower_sqmi','external_upper_sqmi']])}

## What this does and does not establish

- Verified mapped entry direction using FlowDir, digitized geometry, shared nodes and decreasing hydrosequence. Correct-orientation endpoint mismatches over 100 m: {qa['correct_endpoint_mismatches_over_100m']}; reversing orientation gives {qa['reversed_endpoint_mismatches_over_100m']} mismatches. Nodes can also represent nongeometric connections.
- Followed every API page, checked unique identifiers, retained all crossing events, required every requested upstream basin/catchment/navigation response, and reconciled the HUC12 partition.
- Used a pinned, previously saved public DWR basin response. Its original retrieval timestamp is unknown; the provenance record identifies the import time, exact agency query and SHA-256. No private model-grid files are used.
- Network connectivity indicates where generated runoff could reach PV. Actual delivery depends on channel infiltration, ephemeral flow, diversions, storm intensity, reservoir operations and routing. Groundwater contribution can follow different paths.
- EROM is a historical climatological screening proxy. No current-year runoff, channel-loss calibration, recharge quantity or uncertainty probability is claimed.
- Zero-local-area connectors without a mapped catchment are retained only after independently checking the network's local-area attribute is exactly zero; those cases are logged in QA. Any other missing local catchment conservatively makes that inlet's lower contribution zero while retaining its upstream basin in the upper mask.
- Boundary-coincident events and reaches without adjacent-node orientation evidence are explicitly listed in QA; they remain potential sources of incompleteness or positional uncertainty.
- Medium-resolution NHDPlus can omit small or modified channels. The footprint is an estimate for mapped drainage, not proof that all physical contributors are captured.
- Divergent/returning reaches and canals remain flagged in the entry table; unknown allocation prevents a summed inflow estimate.
- Climate adjustment must use this spatial mask as a candidate domain and separately validate hydrologic response. A CIMIS/BCM PET regression is not a runoff multiplier.

## Reproduce and manually check

1. Run the GitHub Actions workflow; raw public-source responses are cached with their exact URLs, parameters, retrieval times and SHA-256 checksums in data/source_manifest.json.
2. For any entry COMID, inspect data/raw/basin_ID.geojson, catchment_ID.geojson and upstream_ID.geojson; compare against results/all_boundary_crossing_events.csv.
3. Load results/contributing_area_bracket.geojson and contributing_huc12.geojson in GIS. Both use WGS84 for exchange; areas are calculated in equal-area EPSG:3310.
4. Review results/topology_orientation_checks.csv, boundary_geometry_sensitivity.csv and qa_checks.json.
5. See docs/CLIMATE_ADJUSTMENT.md before using the mask for BCM/CIMIS adjustments.

## Sources

- [DWR basin layer](https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_B118_CA_GroundwaterBasins/FeatureServer/0)
- [USGS Hydrologic Fabric](https://api.water.usgs.gov/docs/fabric-pygeoapi/)
- [USGS NLDI basin semantics](https://api.water.usgs.gov/docs/nldi/basin/)
- [USGS CVHM2 small watershed release](https://www.sciencebase.gov/catalog/item/62201161d34ee0c6b38a870d)
- [EPA NHDPlusV2 user guide and EROM definitions](https://www.epa.gov/system/files/documents/2023-04/NHDPlusV2_User_Guide.pdf)
- [PVWD drainage context](https://pleasantvalleywaterdistrict.com/about/maps/)
"""
    (OUT / "REPORT.md").write_text(report)
    data = {key: json.loads((OUT / filename).read_text()) for key, filename in {
        "PV": "pv_subbasin.geojson", "lower": "contributing_area_bracket.geojson",
        "hucs": "contributing_huc12.geojson", "events": "boundary_events.geojson",
        "legacy": "legacy_small_watersheds_near_PV.geojson"}.items()}
    brief = (f"Potential external contributing drainage: {qa['external_lower_sqmi']:.1f}â€“"
             f"{qa['external_upper_sqmi']:.1f} sq mi. Mapped network estimate; not actual inflow or recharge.")
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PV runoff and climate adjustment</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>body{margin:0;font:16px/1.5 system-ui;color:#173244;background:#f4f7f9}header,section{max-width:1150px;margin:auto;padding:24px}h1{margin:0 0 10px;font-size:28px}a{color:#155c88}#map{height:65vh;min-height:450px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:8px;text-align:left;border-bottom:1px solid #cedae2}p{max-width:1000px}.notice{background:#fff1cf;padding:14px;border-left:4px solid #b67a17}.scroll{overflow:auto}.links a{margin-right:20px}</style></head><body><header>
<h1>Pleasant Valley runoff and climate adjustment</h1><p>BRIEF</p>
<p class="notice">Green excludes each entry reach's entire local catchment; blue includes it. These are positional drainage-area brackets. EROM runoff proxies represent 1971â€“2000 reach-outlet climatology. No total current-year PV inflow or recharge is estimated.</p>
<p class="links"><a href="https://github.com/jackjing99/pv-runoff-climate-adjustment/blob/main/results/REPORT.md">Full report and assumptions</a><a href="https://github.com/jackjing99/pv-runoff-climate-adjustment/tree/main/results">Download GIS and tables</a><a href="https://github.com/jackjing99/pv-runoff-climate-adjustment">Code and sources</a></p></header><div id="map"></div><section>
<h2>Stream-entry runoff proxies</h2><p>Rows flagged for upstream PV contact are omitted from this display. See the full CSV for all entries and exit/reentry events. Do not sum these reach-outlet values.</p><div class="scroll">TABLE</div>
<h2>What changes from the previous map?</h2><p>The drainage mask follows the mapped upstream network. It does not select watersheds because they lie nearby. Turn on the gray legacy layer to compare the former polygons. HUC12 boundaries are reporting partitions, not independent inlet watersheds.</p>
<p>Built in GitHub Actions from public DWR and USGS sources. No local project files were created.</p></section>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
const data=DATA;
const map=L.map('map');L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'Â© OpenStreetMap contributors',maxZoom:19}).addTo(map);
const upp=L.geoJSON(data.lower,{filter:f=>f.properties.area==='including_whole_entry_catchments',style:{color:'#417ca7',weight:1,fillColor:'#b7d5ea',fillOpacity:.55}}).addTo(map);
const low=L.geoJSON(data.lower,{filter:f=>f.properties.area==='conservative_upstream_catchments',style:{color:'#43866b',weight:1,fillColor:'#70b496',fillOpacity:.6}}).addTo(map);
const hucs=L.geoJSON(data.hucs,{style:{color:'#354f63',weight:.7,fillOpacity:0},onEachFeature:(f,l)=>l.bindPopup(f.properties.name+'<br>'+f.properties.huc12+'<br>External upper area '+f.properties.contributing_upper_sqmi.toFixed(2)+' sq mi')});
const old=L.geoJSON(data.legacy,{style:{color:'#777',weight:1,fillColor:'#999',fillOpacity:.15},onEachFeature:(f,l)=>l.bindPopup('Legacy ID '+f.properties.source_id+'<br>'+f.properties.percent_in_upper_contributing_mask.toFixed(1)+'% in potential contributing mask')});
const pv=L.geoJSON(data.PV,{style:{color:'#a85c0b',weight:3,fillColor:'#efb65b',fillOpacity:.6}}).addTo(map);
const events=L.geoJSON(data.events,{pointToLayer:(f,ll)=>L.circleMarker(ll,{radius:4,color:f.properties.event==='enter'?'#1a6e44':'#a54343',weight:1,fillOpacity:.85}),onEachFeature:(f,l)=>l.bindPopup(f.properties.event+'<br>COMID '+f.properties.comid+'<br>'+f.properties.name)});
L.control.layers(null,{'PV subbasin':pv,'Whole-entry-catchment upper mask':upp,'Upstream-catchment lower mask':low,'HUC12 reporting partitions':hucs,'Stream boundary events':events,'Legacy nearby CVHM2 polygons':old}).addTo(map);
map.fitBounds(upp.getBounds().extend(pv.getBounds()));
L.control.scale({imperial:true,metric:true}).addTo(map);
</script></body></html>"""
    page = page.replace("BRIEF", html.escape(brief)).replace("TABLE", display.to_html(index=False, float_format=lambda x: f"{x:.2f}", border=0)).replace("DATA", json.dumps(data, separators=(",", ":")).replace("</", "<\\/"))
    (DOCS / "index.html").write_text(page)
    (ROOT / "README.md").write_text(
        "# Pleasant Valley runoff and climate adjustment\n\n" + brief +
        "\n\n[Interactive map and report](https://jackjing99.github.io/pv-runoff-climate-adjustment/) Â· "
        "[Full findings and assumptions](results/REPORT.md) Â· [GIS/tables](results/) Â· "
        "[Source manifest](data/source_manifest.json) Â· [QA checks](results/qa_checks.json)\n\n"
        "This reproducible preliminary estimate uses the directed USGS NHDPlusV2 network and the DWR "
        "Pleasant Valley boundary. Nearby polygons are tested against upstream connectivity rather than "
        "assumed to feed PV. External land is counted once by spatial union, and boundary-position "
        "sensitivity is reported.\n\n"
        "The area bracket is not a statistical confidence interval. EROM runoff-based, reference-gage "
        "and gage-adjusted values are historical 1971â€“2000 reach-outlet proxies. They are not current-year "
        "PV boundary inflow or groundwater recharge and must not be summed over nested or reentering reaches.\n\n"
        "## Reproduce\n\nUse Actions â†’ Estimate PV contributing drainage â†’ Run workflow. The entire build "
        "runs on a GitHub-hosted runner; no new files are written to the user's local project. "
        "The workflow pins dependencies, retains public source responses and hashes, checks topology "
        "and spatial accounting, commits results and deploys GitHub Pages.\n\n"
        "## Climate adjustment\n\nSee [the climate-adjustment guidance](docs/CLIMATE_ADJUSTMENT.md). "
        "An ET regression is not a runoff correction factor. Rainfall, PET, runoff generation, channel "
        "delivery and recharge must retain their separate meanings.\n\n"
        "New code is MIT licensed; agency data retain original source notices. No private model grids, "
        "credentials or local drive paths are published.\n")


