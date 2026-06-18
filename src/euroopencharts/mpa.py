from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from .config import EOCConfig, ConfigError
def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: dict[str, Any]) -> Path:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


REQUIRED_MPA_PROPS = [
    "name",
    "source_name",
    "source_url",
    "license",
]

REQUIRED_RULE_KEYS = [
    "zone_id",
    "zone_name",
    "permissions",
    "prohibitions",
    "anchoring",
    "fishing",
    "diving",
    "transit",
]


def process_mpa_layer(config: EOCConfig, root: Path) -> list[Path]:
    """Validate and copy an authoritative MPA layer into the offline dataset.

    The function never creates geometries or rules. If the configured layer is
    enabled but missing and optional, it writes an omission report. If required,
    it fails. If geometry exists and rules are requested but missing, it fails.
    """
    layer = config.layer("marine_protected_areas")
    if not layer.get("enabled", False):
        return [_write_mpa_omission(root, "disabled_by_configuration", config)]

    source_id = layer.get("source_id")
    source_meta = config.source(source_id) if source_id else {}
    path = config.relpath(layer.get("path"))
    rules_path = config.relpath(layer.get("rules_path"))
    required = bool(layer.get("required", False))

    if path is None or not path.exists():
        reason = f"MPA source file not found: {path}" if path else "MPA source path not configured"
        if required:
            raise ConfigError(reason)
        return [_write_mpa_omission(root, reason, config)]

    data = _read_geojson(path)
    _validate_mpa_geojson(data, path)

    rules = None
    if rules_path and rules_path.exists():
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        _validate_rules(rules, rules_path)
    elif layer.get("fail_if_rules_missing_when_geometry_present", True):
        raise ConfigError(f"MPA geometry exists but rules file is missing: {rules_path}")

    features = data.get("features", [])
    acquisition = datetime.now(timezone.utc).isoformat()
    for feature in features:
        props = feature.setdefault("properties", {})
        props.setdefault("source_id", source_id)
        props.setdefault("source_name", source_meta.get("name"))
        props.setdefault("license", source_meta.get("license"))
        props.setdefault("acquisition_timestamp", acquisition)
        props.setdefault("processing_timestamp", acquisition)
        props.setdefault("synthetic", False)
        if rules:
            zone_id = str(props.get("zone_id", props.get("zone", "")))
            if zone_id and zone_id in rules.get("zones", {}):
                props["rules"] = rules["zones"][zone_id]
            elif rules.get("default_rules"):
                props["rules"] = rules["default_rules"]
            else:
                raise ConfigError(f"No MPA rules found for feature zone_id='{zone_id}' in {path}")
        if props.get("synthetic") is True:
            raise ConfigError(f"Synthetic MPA feature is forbidden: {feature.get('id', '<no id>')}")

    outdir = ensure_dir(root / "intermediate" / "derived")
    out = outdir / "marine_protected_areas.geojson"
    out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    opencpn = ensure_dir(root / "offline_bundle" / "opencpn") / "marine_protected_areas.geojson"
    opencpn.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")

    prov = write_json(root / "metadata" / "marine_protected_areas_provenance.json", {
        "layer": "marine_protected_areas",
        "source_id": source_id,
        "source": source_meta,
        "input_path": str(path),
        "rules_path": str(rules_path) if rules_path else None,
        "feature_count": len(features),
        "synthetic_data_used": False,
        "processing_timestamp": acquisition,
        "required": required,
    })
    return [out, opencpn, prov]


def _read_geojson(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection":
        raise ConfigError(f"MPA source must be a GeoJSON FeatureCollection: {path}")
    return data


def _validate_mpa_geojson(data: dict[str, Any], path: Path) -> None:
    for idx, feature in enumerate(data.get("features", [])):
        if feature.get("type") != "Feature":
            raise ConfigError(f"Invalid MPA feature at index {idx} in {path}")
        geom = feature.get("geometry") or {}
        if geom.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ConfigError(f"MPA feature {idx} must be Polygon or MultiPolygon in {path}")
        props = feature.get("properties") or {}
        missing = [key for key in REQUIRED_MPA_PROPS if not props.get(key)]
        if missing:
            raise ConfigError(f"MPA feature {idx} missing required properties {missing} in {path}")


def _validate_rules(rules: dict[str, Any], path: Path) -> None:
    if not isinstance(rules, dict):
        raise ConfigError(f"MPA rules file must contain a JSON object: {path}")
    zones = rules.get("zones", {})
    default_rules = rules.get("default_rules")
    if not zones and not default_rules:
        raise ConfigError(f"MPA rules file must contain zones or default_rules: {path}")
    rule_sets = list(zones.values()) + ([default_rules] if default_rules else [])
    for idx, item in enumerate(rule_sets):
        missing = [key for key in REQUIRED_RULE_KEYS if key not in item]
        if missing:
            raise ConfigError(f"MPA rules entry {idx} missing keys {missing} in {path}")


def _write_mpa_omission(root: Path, reason: str, config: EOCConfig) -> Path:
    return write_json(root / "metadata" / "marine_protected_areas_omitted.json", {
        "layer": "marine_protected_areas",
        "omitted": True,
        "reason": reason,
        "synthetic_data_used": False,
        "configured_required": bool(config.layer("marine_protected_areas").get("required", False)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
