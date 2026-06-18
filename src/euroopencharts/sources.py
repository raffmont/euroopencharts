from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import math
from .model import Area, ensure_dir, write_geojson, write_json


def synthetic_copernicus_bathymetry(area: Area, root: Path, nx: int = 49, ny: int = 49) -> Path:
    """Create a deterministic Copernicus/EMODnet-like gridded depth product.

    This offline prototype does not download live data. The file structure and
    metadata are intentionally compatible with a later replacement by real
    Copernicus Marine and EMODnet download tasks.
    """
    out = ensure_dir(root / "raw" / "copernicus") / "bathymetry_grid.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["lon", "lat", "depth_m", "uncertainty_m", "source"])
        writer.writeheader()
        for iy in range(ny):
            lat = area.south + (area.north - area.south) * iy / (ny - 1)
            for ix in range(nx):
                lon = area.west + (area.east - area.west) * ix / (nx - 1)
                shelf = 25 + 2100 * ((lon - area.west) / (area.east - area.west)) ** 1.8
                coast_effect = 180 * math.exp(-((lat - 40.75) ** 2) / 0.15)
                canyon = 420 * math.exp(-(((lon - 14.15) ** 2) / 0.08 + ((lat - 40.25) ** 2) / 0.20))
                depth = max(2.0, shelf + coast_effect + canyon + 35 * math.sin(3 * lat) * math.cos(2 * lon))
                uncertainty = 1.5 + depth * 0.015
                writer.writerow({
                    "lon": round(lon, 6), "lat": round(lat, 6),
                    "depth_m": round(depth, 2), "uncertainty_m": round(uncertainty, 2),
                    "source": "synthetic-copernicus-emodnet-prototype",
                })
    write_json(root / "raw" / "copernicus" / "provenance.json", {
        "title": "Synthetic Copernicus/EMODnet bathymetry placeholder",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "fair_note": "Prototype product. Replace task with real Copernicus Marine/EMODnet acquisition for production.",
        "license": "MIT for synthetic sample only",
        "area": area.__dict__,
    })
    return out


def synthetic_openseamap_seamarks(area: Area, root: Path) -> Path:
    features = [
        point("light:ischia-porto", 13.947, 40.745, "light", {"name": "Ischia Porto Light", "range_nm": 11, "colour": "white"}),
        point("buoy:capri-north", 14.235, 40.590, "buoy", {"name": "Capri North Cardinal", "category": "cardinal"}),
        point("harbor:napoli", 14.268, 40.840, "harbor", {"name": "Porto di Napoli", "services": "fuel,water,repairs"}),
        point("marina:procida", 14.022, 40.765, "marina", {"name": "Marina di Procida", "services": "water,electricity"}),
        point("anchorage:ventotene-cala-nave", 13.431, 40.798, "anchorage", {"name": "Cala Nave", "shelter_from": "W,NW", "holding": "sand"}),
        point("anchorage:punta-licosa", 14.905, 40.252, "anchorage", {"name": "Punta Licosa", "shelter_from": "N,NE", "holding": "sand"}),
        point("poi:capri-fuel", 14.242, 40.556, "poi", {"name": "Capri nautical services", "category": "services"}),
    ]
    path = root / "raw" / "openseamap" / "seamarks.geojson"
    write_geojson(path, features, name="synthetic-openseamap-seamarks")
    write_json(root / "raw" / "openseamap" / "provenance.json", {
        "title": "Synthetic OpenSeaMap/OSM seamark placeholder",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "license_note": "Real OpenStreetMap/OpenSeaMap data requires ODbL attribution and share-alike handling.",
        "area": area.__dict__,
    })
    return path


def point(fid: str, lon: float, lat: float, kind: str, props: dict) -> dict:
    p = {"id": fid, "kind": kind, "source": "synthetic-openseamap-prototype"}
    p.update(props)
    return {"type": "Feature", "id": fid, "properties": p, "geometry": {"type": "Point", "coordinates": [lon, lat]}}
