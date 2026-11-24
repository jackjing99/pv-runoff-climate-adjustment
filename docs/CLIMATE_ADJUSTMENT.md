# Using the contributing mask for climate adjustment

The drainage estimate selects a defensible **candidate spatial domain**. It does not calibrate BCM runoff or demonstrate delivery to the groundwater basin.

1. Use both lower and upper masks to extract native BCM runoff, recharge, precipitation and PET. For depths, apply fractional pixel-area weighting and retain each pixel's area; runoff volume equals sum(depth_mm / 1000 Ã— intersected_pixel_area_m2). Do not substitute a mean cell value for a basin volume.
2. Preserve source versions, original archives, units, dates, NoData and calendar completeness. Annual totals require twelve complete months; no missing month becomes zero.
3. Compare a baseline with adjustments by calendar month and by official water-year type. Leave entire water years out. Use a chronological holdout before applying a model to future years. Nearby pixels are spatially dependent.
4. CIMIS ETo is grass-reference ET. BCM PET is a different modeled quantity. An empirical ETo/PET equation cannot be used as a multiplier on runoff. Changing PET requires re-running or otherwise validating the hydrologic response.
5. Calibrate runoff generation and channel delivery separately against suitable streamflow and water-budget evidence. Evaluate diversions, storm intermittency, channel infiltration and in-basin losses. Do not equate generated runoff, PV boundary inflow, and aquifer recharge.
6. Report lower/upper drainage-mask sensitivity and named inlet results. HUC12 units split the mask for reporting; they are not independent inlet basins. EROM 1971â€“2000 outlet proxies are screening context, not calibration observations for WY2003â€“2025.

This repository deliberately publishes no adjusted BCM/CIMIS grids or unverified recharge totals. The currently published estimate addresses mapped contributing drainage and historical runoff proxies.
