from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any, Iterable


@dataclass(frozen=True)
class Area:
    name: str
    west: float
    south: float
    east: float
    north: float
    crs: str = "EPSG:4326"

    def to_feature(self) -> dict[str, Any]:
        ring = [
            [self.west, self.south], [self.east, self.south],
            [self.east, self.north], [self.west, self.north],
            [self.west, self.south],
        ]
        return {
            "type": "Feature",
            "properties": asdict(self),
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        }


TYRRHENIAN_EAST = Area(
    name="central-southern-tyrrhenian-east",
    west=12.0,
    south=38.0,
    east=16.2,
    north=42.0,
)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, obj: Any) -> Path:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_geojson(path: Path, features: Iterable[dict[str, Any]], *, name: str) -> Path:
    return write_json(path, {
        "type": "FeatureCollection",
        "name": name,
        "features": list(features),
    })
