# Independent QA review

Reviewed 2026-11-24 by an independent agent with no inherited analysis context. Source implementation: 79c1806870ad2a8762d3fda3ccecfd0360d38689. Published analysis results: 249b9417437fdbe007263c3e4b31a0a1b5616fae.

**Assessment:** No unresolved major computational defect identified in the contributing-area estimate. Independently reconstructed external drainage is **375.3027â€“404.1889 square miles**, agreeing with published results. This is a mapped-network drainage estimate, not measured runoff delivery or groundwater recharge.

## Verified independently

- Pinned DWR boundary identifies Pleasant Valley, basin 5-022.10; its original retrieval timestamp is explicitly unknown.
- Direction checks cover 557 connected reach pairs: zero correct-orientation endpoint mismatches exceeding 100 m, versus 557 when reversed. Every candidate entry reach has adjacent-node evidence.
- Original-boundary results contain 28 entry reaches and 29 entry events. Los Gatos Creek COMID 17150436 enters twice and is explicitly flagged.
- Rebuilt upper and lower masks from raw basin/catchment responses. The lower mask lies entirely within the upper; PV is excluded. Spatial union removes approximately 434.6773 square miles of repeated basin area.
- HUC12 clipped areas reconcile with the complete mask: zero uncovered area and negligible numerical overlap.
- All 111 archived source responses match their manifest SHA-256 hashes and byte counts. All eight original CVHM2 shapefile components match publisher MD5 checksums and sizes.
- Published inlet proxies retain their 1971â€“2000 reach-outlet meaning, with no summed PV inflow.

## Where the legacy proximity selection fails

Percentages describe each original polygon's area **outside PV** intersecting the upper contributing mask.

| Feature index | Legacy ID | Intersection |
|---|---:|---:|
| 5 | 106 | 0.00% |
| 32 | 23 | 15.57% |
| 33 | 24 | 10.43% |
| 54 | 24 | 97.76% |

These values were independently reproduced using original read-only shapefiles whose checksums match the publisher. The two ID 24 polygons must remain distinguishable. Geographic proximity does not establish contributing drainage.

## Interpretation limits

The overlay includes 33 HUC12 reporting intersections. Sixteen are smaller than 0.1 square mile and together cover approximately 0.27 square mile. Small fragments can reflect differences between NHDPlusV2 and 2025 WBD boundaries. The 0.1 threshold is descriptive; it does not select drainage. Complete HUC12 polygons must not replace the clipped mask.

COMID 14883293 has no assigned catchment polygon and an authoritative local-area attribute of zero. Its guarded zero-local-area treatment is appropriate. It is also a minor divergent branch with zero EROM estimates. Those zeros do **not** establish zero runoff generation upstream: default divergence routing can allocate unknown splits entirely to the major branch. Ratios among qa, qc and qe are not independently calibrated channel-delivery fractions.

## Not verified

Actual channel delivery, diversion allocations, omitted small channels, present-year runoff, recharge, or calibration of a BCM/CIMIS adjustment were not established. The area bracket is not a confidence interval or a bound on actual delivered water.

Map appearance and browser interaction were not reviewed by this independent reviewer. Analysis and repository publication succeeded; the reviewed workflow's separate artifact-based GitHub Pages deployment failed. The maintainer subsequently changed publication to the committed docs folder; deployment verification is separate from this independent numerical review.

No local project files were created or modified for this review.

## Authoritative references

- https://api.water.usgs.gov/docs/nldi/basin/
- https://api.water.usgs.gov/docs/fabric-pygeoapi/
- https://www.usgs.gov/national-hydrography/value-added-attributes-vaas
- https://www.epa.gov/system/files/documents/2023-04/NHDPlusV2_User_Guide.pdf
