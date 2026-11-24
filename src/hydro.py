"""Estimate potential external runoff-contributing drainage to Pleasant Valley.

Only GitHub-hosted execution is required. Preserves public source response bytes,
exact queries and hashes. NHDPlus directed-network connectivity identifies entry
basins. The area bracket excludes/includes the whole local entry-reach catchment.
It is not a confidence interval or a bound on actual delivery through diversions.
EROM 1971-2000 outlet flows remain separate proxies and are never totaled over
nested or reentering reaches. HUC12 polygons are reporting partitions only.
"""
from __future__ import annotations
import concurrent.futures as cf
import hashlib
import html
import json
import math
import platform
import time
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely import make_valid, union_all
from shapely.geometry import GeometryCollection, LineString, Point, mapping, shape
from shapely.ops import transform, substring

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
OUT = ROOT / "results"
DOCS = ROOT / "docs"
for folder in (RAW, OUT, DOCS):
    folder.mkdir(parents=True, exist_ok=True)
FABRIC = "https://api.water.usgs.gov/fabric/pygeoapi"
NLDI = "https://api.water.usgs.gov/nldi/linked-data"
M2_PER_SQMI = 2589988.110336
CFS_TO_AFYR = 86400 * 365.25 / 43560
TO_M = Transformer.from_crs(4326, 3310, always_xy=True).transform
TO_LL = Transformer.from_crs(3310, 4326, always_xy=True).transform
SOURCES = []
PROPERTIES = ["comid", "gnis_name", "flowdir", "fromnode", "tonode",
              "hydroseq", "dnhydroseq", "dnminorhyd", "divergence", "rtndiv",
              "dndraincou", "areasqkm", "totdasqkm", "divdasqkm", "ftype",
              "qa_ma", "qc_ma", "qe_ma"] + [
                  f"{prefix}_{month:02}" for prefix in ("qa", "qc", "qe") for month in range(1, 13)]


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def download(name, url, params=None):
    """Cache immutable response bytes on the remote runner, with their provenance."""
    path = RAW / name
    meta_path = RAW / (name + ".request.json")
    if path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        assert meta["requested_url"] == url and meta["parameters"] == (params or {}), "Cached query contract changed; version the source snapshot"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"]
        SOURCES.append(meta)
        return path
    error = None
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=(15, 90),
                                    headers={"User-Agent": "PV-runoff-climate-adjustment research"})
            response.raise_for_status()
            payload = response.content
            assert len(payload) < 45_000_000, "Archive large sources as release artifacts instead of Git objects"
            path.write_bytes(payload)
            meta = {"file": str(path.relative_to(ROOT)), "requested_url": url,
                    "parameters": params or {}, "actual_url": response.url,
                    "retrieved_utc": utc(), "http_status": response.status_code,
                    "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                    "response_headers": dict(response.headers)}
            meta_path.write_text(json.dumps(meta, indent=2))
            SOURCES.append(meta)
            return path
        except (requests.RequestException, AssertionError) as exc:
            error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Source request failed: {name}: {error}")


def get_json(name, url, params=None):
    return json.loads(download(name, url, params).read_bytes())


def collection(name, collection_id, bbox, properties=None):
    """Follow every OGC next link and reconcile unique IDs and numberMatched."""
    url = f"{FABRIC}/collections/{collection_id}/items"
    params = {"f": "json", "bbox": ",".join(f"{v:.9f}" for v in bbox), "limit": 1000}
    if properties:
        params["properties"] = ",".join(properties)
    features, matched, page, seen_urls = [], None, 0, set()
    while url:
        assert url not in seen_urls, "Repeated OGC pagination URL"
        seen_urls.add(url)
        payload = get_json(f"{name}_{page}.geojson", url, params)
        features.extend(payload["features"])
        if page == 0:
            matched = payload.get("numberMatched")
        next_urls = [link["href"] for link in payload.get("links", []) if link.get("rel") == "next"]
        assert len(next_urls) <= 1
        url = urljoin(url, next_urls[0]) if next_urls else None
        params = None
        page += 1
    identifiers = [feature.get("id") for feature in features]
    if all(value is not None for value in identifiers):
        assert len(set(identifiers)) == len(identifiers), "Duplicate feature ID across pages"
    if matched is not None:
        assert len(features) == int(matched), f"Incomplete collection {name}"
    return {"type": "FeatureCollection", "features": features}


def geometry(feature_collection):
    return make_valid(union_all([shape(feature["geometry"]) for feature in feature_collection["features"]]))


def save_geojson(path, features):
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features},
                               separators=(",", ":"), allow_nan=False))


def geo_feature(geom, properties):
    return {"type": "Feature", "properties": properties,
            "geometry": mapping(transform(TO_LL, geom))}


def normalize_line(geom):
    """Preserve digitized order; fail for disconnected/reversed multipart sources."""
    if geom.geom_type == "LineString":
        return geom
    assert geom.geom_type == "MultiLineString"
    parts = list(geom.geoms)
    coordinates = list(parts[0].coords)
    for part in parts[1:]:
        assert Point(coordinates[-1]).distance(Point(part.coords[0])) < 0.1, (
            "Unordered/disconnected multipart reach requires explicit review")
        coordinates.extend(list(part.coords)[1:])
    return LineString(coordinates)


def points_from_intersection(inter):
    if inter.is_empty:
        return []
    if inter.geom_type == "Point":
        return [inter]
    if inter.geom_type in ("MultiPoint", "GeometryCollection"):
        return [pt for piece in inter.geoms for pt in points_from_intersection(piece)]
    return []


def crossings(lines, target, inset_m):
    events = []
    for comid, row in lines.items():
        line = row["line"]
        intersection = line.intersection(target.boundary)
        points = points_from_intersection(intersection)
        if intersection.length > 0:
            events.append({"comid": comid, "inset_m": inset_m, "event": "boundary_coincident",
                           "distance_along_m": None, "x": None, "y": None})
        distances = sorted(set(round(line.project(point), 6) for point in points))
        for i, distance in enumerate(distances):
            gap = min(distance - (distances[i-1] if i else 0),
                      (distances[i+1] if i+1 < len(distances) else line.length) - distance)
            step = min(5.0, gap/3) if gap > 0 else 0
            point = line.interpolate(distance)
            if step <= 1e-5 or distance < 1e-5 or line.length-distance < 1e-5:
                kind = "endpoint_uncertain"
            else:
                before = target.contains(line.interpolate(distance-step))
                after = target.contains(line.interpolate(distance+step))
                kind = "enter" if not before and after else "exit" if before and not after else "tangent"
            events.append({"comid": comid, "inset_m": inset_m, "event": kind,
                           "distance_along_m": distance, "x": point.x, "y": point.y})
    return events


def topology_qa(lines):
    by_from = defaultdict(list)
    for comid, row in lines.items():
        by_from[int(row["properties"]["fromnode"])].append(comid)
    records = []
    for upstream, row in lines.items():
        for downstream in by_from.get(int(row["properties"]["tonode"]), []):
            other = lines[downstream]
            records.append({"upstream_comid": upstream, "downstream_comid": downstream,
                            "correct_endpoint_gap_m": Point(row["line"].coords[-1]).distance(
                                Point(other["line"].coords[0])),
                            "reversed_endpoint_gap_m": Point(row["line"].coords[0]).distance(
                                Point(other["line"].coords[-1])),
                            "hydroseq_decreases": row["properties"]["hydroseq"] > other["properties"]["hydroseq"]})
    frame = pd.DataFrame(records)
    assert len(frame) >= 20, "Insufficient independent topology evidence"
    assert frame.correct_endpoint_gap_m.median() < frame.reversed_endpoint_gap_m.median()
    assert frame.hydroseq_decreases.all(), "Coordinate direction conflicts with hydrologic sequence"
    frame.to_csv(OUT / "topology_orientation_checks.csv", index=False)
    return {"node_pairs_checked": len(frame),
            "correct_endpoint_mismatches_over_100m": int((frame.correct_endpoint_gap_m > 100).sum()),
            "reversed_endpoint_mismatches_over_100m": int((frame.reversed_endpoint_gap_m > 100).sum()),
            "all_hydroseq_decreases": bool(frame.hydroseq_decreases.all())}


def inlet_sources(comid):
    basin = get_json(f"basin_{comid}.geojson", f"{NLDI}/comid/{comid}/basin",
                     {"f": "json", "simplified": "false", "splitCatchment": "false"})
    local = get_json(f"catchment_{comid}.geojson", f"{FABRIC}/collections/catchmentsp/items",
                     {"featureid": comid, "f": "json", "limit": 2})
    if len(local["features"]) == 1:
        assert int(local["features"][0]["properties"]["featureid"]) == comid, "Catchment identifier mismatch"
        local_method = "native_mapped_local_catchment"
    elif len(local["features"]) == 0 and local.get("numberMatched") == 0:
        network = get_json(f"catchmentless_reach_{comid}.geojson",
                           f"{FABRIC}/collections/nhdflowline_network/items",
                           {"comid": comid, "f": "json", "limit": 2})
        assert len(network["features"]) == 1 and int(network["features"][0]["properties"]["comid"]) == comid
        local_method = ("no_assigned_local_catchment_zero_area_in_network"
                        if float(network["features"][0]["properties"]["areasqkm"]) == 0
                        else "unresolved_local_catchment_conservative_whole_basin")
    else:
        raise AssertionError(f"Unexpected catchment response {comid}: count={len(local['features'])}")
    upstream = get_json(f"upstream_{comid}.geojson",
                        f"{NLDI}/comid/{comid}/navigation/UT/flowlines",
                        {"f": "json", "distance": 1000})
    upstream_ids = {int(feature["properties"]["nhdplus_comid"]) for feature in upstream["features"]}
    assert comid in upstream_ids, "Upstream navigation omitted the starting reach"
    basin_m = transform(TO_M, geometry(basin))
    local_m = (transform(TO_M, geometry(local)) if local_method == "native_mapped_local_catchment"
               else GeometryCollection() if local_method == "no_assigned_local_catchment_zero_area_in_network"
               else basin_m)
    fraction = local_m.intersection(basin_m).area/local_m.area if local_m.area > 0 else 1.0
    assert fraction >= 0.99, f"Local catchment not contained in basin {comid}: {fraction}"
    return comid, {"basin": basin_m, "local": local_m, "upstream_ids": upstream_ids,
                   "local_in_basin_fraction": fraction, "local_catchment_method": local_method}


def finite_flow(value):
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= 0 else None

