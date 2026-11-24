# Pleasant Valley runoff and climate adjustment

Potential external contributing drainage: 375.3â€“404.2 sq mi. Mapped network estimate; not actual inflow or recharge.

[Interactive map and report](https://jackjing99.github.io/pv-runoff-climate-adjustment/) Â· [Full findings and assumptions](results/REPORT.md) Â· [GIS/tables](results/) Â· [Source manifest](data/source_manifest.json) Â· [QA checks](results/qa_checks.json)

This reproducible preliminary estimate uses the directed USGS NHDPlusV2 network and the DWR Pleasant Valley boundary. Nearby polygons are tested against upstream connectivity rather than assumed to feed PV. External land is counted once by spatial union, and boundary-position sensitivity is reported.

The area bracket is not a statistical confidence interval. EROM runoff-based, reference-gage and gage-adjusted values are historical 1971â€“2000 reach-outlet proxies. They are not current-year PV boundary inflow or groundwater recharge and must not be summed over nested or reentering reaches.

## Reproduce

Use Actions â†’ Estimate PV contributing drainage â†’ Run workflow. The entire build runs on a GitHub-hosted runner; no new files are written to the user's local project. The workflow pins dependencies, retains public source responses and hashes, checks topology and spatial accounting, commits results and deploys GitHub Pages.

## Climate adjustment

See [the climate-adjustment guidance](docs/CLIMATE_ADJUSTMENT.md). An ET regression is not a runoff correction factor. Rainfall, PET, runoff generation, channel delivery and recharge must retain their separate meanings.

New code is MIT licensed; agency data retain original source notices. No private model grids, credentials or local drive paths are published.
