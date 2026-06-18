from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from urllib.parse import urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import EOCConfig, ConfigError

PLACEHOLDER_MARKERS = ("example.invalid", "replace-with-")


def download_configured_sources(config: EOCConfig, root: Path) -> list[Path]:
    """Download source files declared by the single JSON configuration file."""
    written: list[Path] = []
    written.append(validate_high_resolution_sources(config, root))
    downloads = config.data.get("source_downloads", [])
    if not isinstance(downloads, list):
        raise ConfigError("source_downloads must be a list when present")
    for item in downloads:
        written.extend(_download_one(config, root, item))
    return written


def validate_high_resolution_sources(config: EOCConfig, root: Path) -> Path:
    """Require explicit high-resolution metadata for every configured source."""
    checked: list[dict] = []
    source_ids = set()
    for layer in config.data.get("layers", {}).values():
        if isinstance(layer, dict) and layer.get("enabled", False) and layer.get("source_id"):
            source_ids.add(layer["source_id"])
    for item in config.data.get("source_downloads", []):
        if isinstance(item, dict) and item.get("source_id"):
            source_ids.add(item["source_id"])

    for source_id in sorted(source_ids):
        source = config.source(source_id)
        if not source:
            raise ConfigError(f"Configured high-resolution source '{source_id}' is not defined in sources")
        quality = source.get("quality")
        if not isinstance(quality, dict):
            raise ConfigError(f"Source '{source_id}' must declare a quality block")
        resolution_class = quality.get("resolution_class")
        if resolution_class not in {"high", "very_high"}:
            raise ConfigError(f"Source '{source_id}' must declare high or very_high resolution_class")
        if not quality.get("intended_use"):
            raise ConfigError(f"Source '{source_id}' must declare quality.intended_use")
        if not any(k in quality for k in ("grid_resolution_arc_seconds", "pixel_resolution_arc_seconds", "nominal_scale", "feature_resolution")):
            raise ConfigError(
                f"Source '{source_id}' must declare a measurable quality resolution or scale"
            )
        freshness = source.get("freshness")
        if quality.get("requires_current_extract") is True:
            if not isinstance(freshness, dict):
                raise ConfigError(f"Source '{source_id}' must declare freshness metadata for current extracts")
            for key in ["maximum_age_days", "acquired_at_field", "update_policy"]:
                if not freshness.get(key):
                    raise ConfigError(f"Source '{source_id}' must declare freshness.{key}")
        checked.append({
            "source_id": source_id,
            "name": source.get("name"),
            "quality": quality,
            "freshness": freshness,
        })

    manifest = root / "metadata" / "source_quality_requirements.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "Every enabled/downloadable source must explicitly declare high-resolution quality metadata; no low-resolution or undocumented source is silently accepted.",
        "sources_checked": checked,
    }, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def _download_one(config: EOCConfig, root: Path, item: dict) -> list[Path]:
    if not isinstance(item, dict):
        raise ConfigError("Each source_downloads entry must be an object")
    for key in ["source_id", "url", "target"]:
        if key not in item:
            raise ConfigError(f"source_downloads entry missing '{key}'")

    source_id = item["source_id"]
    source = config.source(source_id)
    if not source:
        raise ConfigError(f"Downloaded source '{source_id}' is not defined in sources")
    if not source.get("license"):
        raise ConfigError(f"Downloaded source '{source_id}' must declare license metadata")

    target = config.relpath(item["target"])
    assert target is not None
    target = target.resolve()
    if not _is_inside_any(target, _allowed_write_roots(config, root)):
        raise ConfigError(f"Download target must stay inside the project/config tree: {target}")

    required = bool(item.get("required", True))
    manifest_path = root / "metadata" / "source_downloads" / f"{source_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if item.get("provider") == "overpass_seamarks":
        return _download_overpass_seamarks(config, root, item, target, manifest_path, source, required)

    if _is_placeholder_url(item["url"]):
        if required:
            raise ConfigError(f"Required source '{source_id}' still uses a placeholder URL: {item['url']}")
        manifest_path.write_text(json.dumps({
            "source_id": source_id,
            "url": item["url"],
            "target": str(target),
            "status": "configuration_required",
            "required": False,
            "reason": "Placeholder URL must be replaced with an official source URL before download",
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }, indent=2, sort_keys=True), encoding="utf-8")
        return [manifest_path]

    if target.exists() and item.get("skip_existing", True):
        status = "existing"
    else:
        try:
            _fetch(item["url"], target, int(item.get("timeout_seconds", 120)))
            status = "downloaded"
        except (OSError, URLError, TimeoutError) as exc:
            if required:
                raise RuntimeError(f"Required source download failed for {source_id}: {item['url']}: {exc}") from exc
            manifest_path.write_text(json.dumps({
                "source_id": source_id,
                "url": item["url"],
                "target": str(target),
                "status": "omitted",
                "required": False,
                "reason": str(exc),
                "created_utc": datetime.now(timezone.utc).isoformat(),
            }, indent=2, sort_keys=True), encoding="utf-8")
            return [manifest_path]

    digest = _sha256(target)
    manifest_path.write_text(json.dumps({
        "source_id": source_id,
        "source": source,
        "url": item["url"],
        "target": str(target),
        "status": status,
        "required": required,
        "sha256": digest,
        "bytes": target.stat().st_size,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2, sort_keys=True), encoding="utf-8")
    return [target, manifest_path]


def _fetch(url: str, target: Path, timeout_seconds: int) -> None:
    with urlopen(url, timeout=timeout_seconds) as response:
        data = response.read()
    target.write_bytes(data)


def _download_overpass_seamarks(
    config: EOCConfig,
    root: Path,
    item: dict,
    target: Path,
    manifest_path: Path,
    source: dict,
    required: bool,
) -> list[Path]:
    query = _overpass_query(config)
    timeout = int(item.get("timeout_seconds", 180))
    url = item.get("url", "https://overpass-api.de/api/interpreter")
    try:
        data = _fetch_overpass(url, query, timeout)
        geojson = _overpass_to_geojson(data, config)
        target.write_text(json.dumps(geojson, indent=2, sort_keys=True), encoding="utf-8")
    except (OSError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        if required:
            raise RuntimeError(f"Required OpenStreetMap/OpenSeaMap Overpass download failed: {url}: {exc}") from exc
        manifest_path.write_text(json.dumps({
            "source_id": item["source_id"],
            "url": url,
            "target": str(target),
            "status": "omitted",
            "required": False,
            "reason": str(exc),
            "provider": "overpass_seamarks",
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }, indent=2, sort_keys=True), encoding="utf-8")
        return [manifest_path]

    digest = _sha256(target)
    manifest_path.write_text(json.dumps({
        "source_id": item["source_id"],
        "source": source,
        "url": url,
        "target": str(target),
        "status": "downloaded",
        "required": required,
        "provider": "overpass_seamarks",
        "query": query,
        "feature_count": len(geojson["features"]),
        "sha256": digest,
        "bytes": target.stat().st_size,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2, sort_keys=True), encoding="utf-8")
    return [target, manifest_path]


def _fetch_overpass(url: str, query: str, timeout_seconds: int) -> dict:
    body = urlencode({"data": query}).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _overpass_query(config: EOCConfig) -> str:
    area = config.area
    south, west, north, east = area["south"], area["west"], area["north"], area["east"]
    bbox = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:180];
(
  node["seamark:type"]({bbox});
  way["seamark:type"]({bbox});
  relation["seamark:type"]({bbox});
  node["harbour"]({bbox});
  way["harbour"]({bbox});
  relation["harbour"]({bbox});
  node["leisure"="marina"]({bbox});
  way["leisure"="marina"]({bbox});
  relation["leisure"="marina"]({bbox});
  node["natural"="bay"]({bbox});
  way["natural"="bay"]({bbox});
  relation["natural"="bay"]({bbox});
  node["mooring"]({bbox});
  way["mooring"]({bbox});
  relation["mooring"]({bbox});
);
out tags center geom;
""".strip()


def _overpass_to_geojson(data: dict, config: EOCConfig) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    features = []
    for element in data.get("elements", []):
        geometry = _element_geometry(element)
        if geometry is None:
            continue
        tags = element.get("tags", {})
        props = {
            "source": "OpenStreetMap/OpenSeaMap Overpass API",
            "source_url": "https://www.openstreetmap.org/copyright",
            "license": "Open Database License (ODbL)",
            "acquisition_timestamp": timestamp,
            "osm_type": element.get("type"),
            "osm_id": element.get("id"),
            "feature_class": _feature_class(tags),
            "synthetic": False,
        }
        props.update(tags)
        features.append({
            "type": "Feature",
            "id": f"{element.get('type')}/{element.get('id')}",
            "properties": props,
            "geometry": geometry,
        })
    return {
        "type": "FeatureCollection",
        "name": f"{config.area.get('id', 'aoi')}-openseamap-osm-current-extract",
        "synthetic_data_used": False,
        "features": features,
    }


def _element_geometry(element: dict) -> dict | None:
    if "lon" in element and "lat" in element:
        return {"type": "Point", "coordinates": [element["lon"], element["lat"]]}
    center = element.get("center")
    if center:
        return {"type": "Point", "coordinates": [center["lon"], center["lat"]]}
    geom = element.get("geometry")
    if geom:
        coords = [[p["lon"], p["lat"]] for p in geom if "lon" in p and "lat" in p]
        if len(coords) >= 4 and coords[0] == coords[-1]:
            return {"type": "Polygon", "coordinates": [coords]}
        if len(coords) >= 2:
            return {"type": "LineString", "coordinates": coords}
    return None


def _feature_class(tags: dict) -> str:
    seamark = tags.get("seamark:type")
    if seamark:
        return str(seamark)
    if tags.get("leisure") == "marina":
        return "marina"
    if tags.get("natural") == "bay":
        return "bay"
    if "harbour" in tags:
        return "harbor"
    if "mooring" in tags:
        return "mooring"
    return "nautical_feature"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_inside_any(path: Path, parents: list[Path]) -> bool:
    return any(_is_inside(path, parent) for parent in parents)


def _allowed_write_roots(config: EOCConfig, root: Path) -> list[Path]:
    roots = [config.path.parent, root]
    project_root = _find_project_root(config.path.parent)
    if project_root is not None:
        roots.append(project_root)
    return roots


def _find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "src").exists():
            return candidate
    return None


def _is_placeholder_url(url: str) -> bool:
    return any(marker in url for marker in PLACEHOLDER_MARKERS)
