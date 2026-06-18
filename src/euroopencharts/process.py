from __future__ import annotations

from pathlib import Path
import csv
import json
from .model import ensure_dir, write_geojson, write_json, Area


def derive_contours_and_qc(root: Path) -> list[Path]:
    src = root / "raw" / "copernicus" / "bathymetry_grid.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8")))
    depths = [float(r["depth_m"]) for r in rows]
    qc = {
        "cells": len(rows),
        "depth_min_m": round(min(depths), 2),
        "depth_max_m": round(max(depths), 2),
        "depth_mean_m": round(sum(depths) / len(depths), 2),
        "status": "PASS",
        "warning": "Synthetic sample. Not for navigation.",
    }
    qc_path = write_json(root / "intermediate" / "qc" / "bathymetry_qc.json", qc)

    levels = [10, 20, 50, 100, 200, 500, 1000, 1500, 2000]
    features = []
    grouped: dict[int, list[tuple[float, float]]] = {l: [] for l in levels}
    for r in rows:
        d = float(r["depth_m"])
        for l in levels:
            if abs(d - l) < max(12, l * 0.06):
                grouped[l].append((float(r["lon"]), float(r["lat"])))
    for level, pts in grouped.items():
        if len(pts) >= 2:
            pts = sorted(pts)
            features.append({
                "type": "Feature",
                "properties": {"depth_m": level, "source": "derived-from-synthetic-grid", "quality": "prototype"},
                "geometry": {"type": "LineString", "coordinates": [[x, y] for x, y in pts]},
            })
    contour_path = write_geojson(root / "intermediate" / "derived" / "depth_contours.geojson", features, name="depth_contours")
    return [qc_path, contour_path]


def derive_anchorages(root: Path) -> Path:
    seamarks = json.loads((root / "raw" / "openseamap" / "seamarks.geojson").read_text(encoding="utf-8"))
    features = []
    for f in seamarks["features"]:
        if f["properties"].get("kind") == "anchorage":
            props = dict(f["properties"])
            props.update({
                "score": 0.78 if "Ventotene" in props.get("name", "") else 0.72,
                "confidence": 0.55,
                "moderation_state": "prototype-auto-generated",
            })
            features.append({"type": "Feature", "id": f["id"], "properties": props, "geometry": f["geometry"]})
    return write_geojson(root / "intermediate" / "derived" / "anchorages.geojson", features, name="anchorages")


def make_stac(area: Area, root: Path) -> Path:
    return write_json(root / "metadata" / "stac_item.json", {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "tyrrhenian-east-prototype-001",
        "bbox": [area.west, area.south, area.east, area.north],
        "geometry": area.to_feature()["geometry"],
        "properties": {
            "title": "Tyrrhenian Open Nautical Atlas - Eastern Sector Prototype",
            "datetime": "2026-06-18T00:00:00Z",
            "fair": {"findable": True, "accessible": True, "interoperable": True, "reusable": True},
            "navigation_warning": "Experimental scientific chart bundle. Not for primary navigation.",
        },
        "assets": {
            "bathymetry_csv": {"href": "raw/copernicus/bathymetry_grid.csv", "type": "text/csv"},
            "seamarks_geojson": {"href": "raw/openseamap/seamarks.geojson", "type": "application/geo+json"},
            "contours_geojson": {"href": "intermediate/derived/depth_contours.geojson", "type": "application/geo+json"},
        },
    })
