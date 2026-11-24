# Pleasant Valley potential runoff-contributing drainage

Preliminary network estimate completed 2026-11-24T20:50:00+00:00. Source snapshots and all derivation code are included in this public repository. Computation occurred on a GitHub-hosted runner.

## Main estimate

**External contributing land: 375.3â€“404.2 square miles**, before any allowance for losses, diversions or transmission failure. PV itself (75.31 square miles) is excluded.

The lower mask includes whole catchments upstream of each boundary-crossing reach but excludes that reach's entire local catchment. The upper mask includes the whole local catchment. This bracket describes uncertainty in the exact stream-entry position within a mapped reach. It is **not** a statistical confidence interval or a bound on actual delivered runoff.

The directed network identifies 28 entry reaches and 29 entry events. Their upstream basins overlap: spatial union removes 434.7 square miles that would otherwise be counted repeatedly. Reentries remain in the area union because they may receive additional exterior drainage.

## Runoff-based inlet evidence

EROM qa is conservatively accumulated flow from modeled runoff. qc is a reference-gage-adjusted natural-flow proxy; qe is a gage-adjusted proxy. These are **1971â€“2000 mean flows in cubic feet per second at the downstream end of each NHDPlus reach**, not observations or present-year flux at the exact PV boundary.

The following table filters reaches flagged as having an upstream PV interior contact. This helps interpretation, but is not a complete independent set of watershed fluxes. Named upstream streams are restricted to the local query window. **Do not sum these rows:** divergent branches, nested drainage and boundary reentries can share contributing areas. Full entry and exit details are in the CSVs.

| comid | reach_name | upstream_named_streams_in_local_window | external_lower_sqmi | external_upper_sqmi | qa_runoff_cfs_1971_2000_outlet | qe_gage_adjusted_cfs_1971_2000_outlet |
| --- | --- | --- | --- | --- | --- | --- |
| 14883295 | Los Gatos Creek | Los Gatos Creek; Mud Run; White Creek | 105.85 | 106.03 | 40.31 | 9.34 |
| 17150452 | Unnamed reach 17150452 | Kolingo Creek; Warthan Creek | 113.64 | 113.99 | 33.58 | 21.00 |
| 948030218 | Jacalitos Creek | Jacalitos Creek; Jasper Creek; Salt Creek; Taylor Creek | 58.96 | 65.26 | 12.29 | 6.94 |
| 17150550 | Unnamed reach 17150550 | Arroyo Pinoso; Beltran Creek; La Jolla Creek | 41.30 | 42.18 | 7.85 | 4.23 |
| 948030220 | Unnamed reach 948030220 |  | 6.55 | 6.93 | 1.37 | 0.62 |
| 14885681 | Unnamed reach 14885681 |  | 2.90 | 4.88 | 1.23 | 0.55 |
| 14883323 | Unnamed reach 14883323 |  | 3.32 | 3.78 | 0.75 | 0.32 |
| 17150594 | Unnamed reach 17150594 | Canoas Creek | 11.11 | 12.13 | 0.56 | 0.23 |
| 17150392 | Unnamed reach 17150392 |  | 6.75 | 7.16 | 0.45 | 0.18 |
| 17150610 | Unnamed reach 17150610 |  | 7.74 | 8.08 | 0.28 | 0.11 |
| 14883191 | Oil Creek | Oil Creek | 4.23 | 5.04 | 0.28 | 0.11 |
| 14883351 | Unnamed reach 14883351 |  | 1.23 | 1.47 | 0.11 | 0.04 |
| 17150388 | Unnamed reach 17150388 |  | 1.48 | 1.50 | 0.06 | 0.02 |
| 14883301 | Unnamed reach 14883301 |  | 0.00 | 1.16 | 0.06 | 0.02 |
| 14885735 | Unnamed reach 14885735 |  | 0.00 | 1.88 | 0.05 | 0.02 |
| 17152188 | Unnamed reach 17152188 |  | 0.00 | 0.94 | 0.05 | 0.01 |
| 14883395 | Unnamed reach 14883395 |  | 0.27 | 0.89 | 0.04 | 0.01 |
| 17150382 | Unnamed reach 17150382 |  | 0.68 | 0.85 | 0.04 | 0.01 |
| 17150386 | Unnamed reach 17150386 |  | 0.00 | 0.53 | 0.03 | 0.01 |
| 17150450 | Unnamed reach 17150450 | Kolingo Creek; Warthan Creek | 113.64 | 114.13 | 0.02 | 0.01 |
| 14883291 | Unnamed reach 14883291 |  | 0.00 | 0.29 | 0.01 | 0.00 |
| 14883189 | Unnamed reach 14883189 |  | 0.00 | 0.26 | 0.01 | 0.00 |
| 948030012 | Unnamed reach 948030012 |  | 0.00 | 0.26 | 0.01 | 0.00 |
| 17150384 | Unnamed reach 17150384 |  | 0.18 | 0.28 | 0.01 | 0.00 |

## Small-watershed reporting units

HUC12 polygons partition the contributing mask for reporting and climate-data extraction. They are not automatically separate inlet basins. The overlay intersects 33 HUC12 reporting units, including small boundary slivers. A presentation flag identifies intersections below 0.1 square mile; this threshold does not select or exclude drainage and all intersections are retained for area accounting. Small overlaps can reflect differences between the 2025 WBD and the NHDPlus basin boundaries. They do not prove that the whole named HUC12 contributes. Use the clipped mask, never the union of the complete HUC12 polygons. Coverage and overlap reconcile in qa_checks.json.

| huc12 | name | contributing_lower_sqmi | contributing_upper_sqmi |
| --- | --- | --- | --- |
| 180300120302 | Upper Warthan Creek | 45.85 | 45.85 |
| 180300120602 | White Creek | 41.52 | 41.52 |
| 180300120604 | Middle Los Gatos Creek | 33.74 | 40.39 |
| 180300120303 | Middle Warthan Creek | 31.18 | 31.18 |
| 180300120401 | Upper Jacalitos Creek | 29.81 | 29.81 |
| 180300120601 | Headwaters Los Gatos Creek | 28.48 | 28.48 |
| 180300120603 | Upper Los Gatos Creek | 22.01 | 22.01 |
| 180300120503 | Canoas Creek | 18.83 | 20.45 |
| 180300120304 | Lower Warthan Creek | 19.37 | 19.74 |
| 180300120502 | Middle Zapato Chino Creek | 19.61 | 19.61 |
| 180300120403 | Lower Jacalitos Creek | 11.87 | 18.18 |
| 180300120501 | Upper Zapato Chino Creek | 17.95 | 17.95 |
| 180300120504 | Lower Zapato Chino Creek | 7.52 | 17.66 |
| 180300120402 | Middle Jacalitos Creek | 17.25 | 17.25 |
| 180300120301 | Hot Springs Canyon | 17.16 | 17.16 |
| 180300120605 | Oil Creek | 12.92 | 16.14 |
| 180300120606 | Lower Los Gatos Creek | 0.03 | 0.53 |
| 180300122303 | 180300122303-Frontal Tulare Lake Bed | 0.00 | 0.06 |
| 180600040201 | Little Cholame Creek | 0.03 | 0.03 |
| 180300121801 | Big Tar Creek | 0.02 | 0.03 |
| 180300121701 | Upper Avenal Creek | 0.02 | 0.02 |
| 180600050902 | Upper Lewis Creek | 0.02 | 0.02 |
| 180300090602 | Lake los Nietos | 0.01 | 0.02 |
| 180600050502 | Upper Big Sandy Creek | 0.02 | 0.02 |
| 180600051101 | Pancho Rico Creek | 0.02 | 0.02 |
| 180600020501 | Clear Creek-San Benito River | 0.02 | 0.02 |
| 180300090604 | Domengine Creek | 0.01 | 0.01 |
| 180300090603 | Salt Creek | 0.01 | 0.01 |
| 180600050901 | North Fork Lewis Creek | 0.01 | 0.01 |
| 180600051001 | Headwaters San Lorenzo Creek  | 0.01 | 0.01 |
| 180300122301 | Arroyo Vadoso | 0.00 | 0.01 |
| 180300090601 | Upper Cantua Creek | 0.01 | 0.01 |
| 180300090606 | 180300090607 | 0.00 | 0.00 |

## Comparison with the legacy nearby CVHM2 polygons

The earlier rule selected any polygon within 1.5 km of PV. This table checks those same source polygons against the network-derived mask; an ID may occur on multiple polygons. The percentages refer to the part outside PV.

| source_id | feature_index | percent_in_upper_contributing_mask | contributing_lower_sqmi | contributing_upper_sqmi |
| --- | --- | --- | --- | --- |
| 106 | 5 | 0.00 | 0.00 | 0.00 |
| 23 | 32 | 15.57 | 12.99 | 16.22 |
| 24 | 33 | 10.43 | 19.59 | 20.09 |
| 24 | 54 | 97.76 | 173.60 | 179.33 |

A high intersection percentage indicates mapped upstream connectivity, not a measured delivery fraction. A low percentage demonstrates why proximity alone cannot identify PV contributors. The CVHM2 layer represents foothill boundary-flow areas for the regional model and is not complete drainage coverage for PV.

## Boundary geometry sensitivity

Inward offsets test alignment differences between the groundwater-basin outline and medium-resolution stream geometry. The original boundary remains the main estimate. Insetting can remove genuine boundary-following channels; it does not establish which boundary interpretation is correct.

| boundary_inset_m | n_entry_reaches | external_lower_sqmi | external_upper_sqmi |
| --- | --- | --- | --- |
| 0 | 28 | 375.30 | 404.19 |
| 100 | 25 | 368.55 | 397.02 |
| 250 | 25 | 378.95 | 398.59 |

## What this does and does not establish

- Verified mapped entry direction using FlowDir, digitized geometry, shared nodes and decreasing hydrosequence. Correct-orientation endpoint mismatches over 100 m: 0; reversing orientation gives 557 mismatches. Nodes can also represent nongeometric connections.
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
