# Pleasant Valley runoff and climate adjustment

A reproducible estimate of **potential external drainage contributing runoff to Pleasant Valley groundwater subbasin 5-022.10**, using public DWR boundaries and the directed USGS NHDPlusV2 network. This project replaces a nearby-polygon assumption with upstream connectivity evidence.

**Initial build in progress.** The GitHub Actions workflow generates the report, map, source manifest, upstream masks and QA checks entirely on a GitHub-hosted runner. No new files are written to the user's local project.

## Scope

- Find every mapped stream entry into PV; retain exit, reentry, tangency and direction QA.
- Delineate potential contributing land with NLDI upstream basins and native local catchments.
- Report an area bracket that excludes/includes the entire boundary-crossing reach's local catchment; this is positional uncertainty, not a statistical confidence interval.
- Intersect the drainage mask with HUC12 reporting units and compare the legacy CVHM2 small-watershed polygons.
- Report NHDPlus EROM runoff/reference-gage/gage-adjusted **1971â€“2000 reach-outlet climatology** as separate proxies. Do not sum nested/reentering reaches or claim current-year inflow or recharge.
- Preserve raw public API responses, exact queries, retrieval dates and SHA-256 checksums.

The project supports choosing spatial domains for later BCM/CIMIS climate adjustment. It does not infer that an empirical PET/ETo correction can be applied directly to runoff, or that all upstream runoff arrives at PV.

## Run

Use **Actions â†’ Estimate PV contributing drainage â†’ Run workflow**. The runner uses Python 3.12 and the pinned requirements. Results are committed under `results/`; the interactive report is published using GitHub Pages. Local execution is optional, not needed for this project.

## Public sources

- DWR Bulletin 118 basin layer: https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_B118_CA_GroundwaterBasins/FeatureServer/0
- USGS Hydrologic Fabric: https://api.water.usgs.gov/docs/fabric-pygeoapi/
- USGS NLDI upstream basin semantics: https://api.water.usgs.gov/docs/nldi/basin/
- USGS CVHM2 small watersheds: https://www.sciencebase.gov/catalog/item/62201161d34ee0c6b38a870d
- EPA NHDPlusV2 user guide: https://www.epa.gov/system/files/documents/2023-04/NHDPlusV2_User_Guide.pdf
- Local drainage context: https://pleasantvalleywaterdistrict.com/about/maps/

All new code is MIT licensed. Public agency source data retain their original notices. No private model files, credentials, or local drive paths are published.
