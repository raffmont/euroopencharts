from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from .config import ConfigError, EOCConfig, load_config
from .downloads import download_configured_sources


PLACEHOLDER_MARKERS = ("example.invalid", "replace-with-")


@dataclass(frozen=True)
class PreparationResult:
    outputs: list[Path]
    manifest: Path
    ready: bool


def prepare_high_quality_run(
    config_path: str | Path = "config.json",
    *,
    strict: bool = False,
    write_config: bool = False,
) -> PreparationResult:
    """Prepare configured official sources for a high-quality actual-data run.

    This function never invents data or substitutes placeholder layers. It only
    downloads URLs declared in the single JSON configuration file, records
    missing optional sources, validates freshness and OpenBridge symbols, and
    optionally persists URL replacements derived from explicit configured
    `official_url` values.
    """
    config = load_config(config_path)
    outputs: list[Path] = []
    if write_config:
        _rewrite_configured_official_urls(config)
        config = load_config(config.path)

    root = config.data_root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    _fail_on_required_placeholders(config)
    outputs.extend(download_configured_sources(config, root))
    checks = {
        "source_downloads": _inspect_source_downloads(config),
        "freshness": _inspect_freshness(config),
        "marine_protected_areas": _inspect_mpa_inputs(config),
        "openbridge_symbols": _inspect_openbridge_symbols(config),
    }
    ready = _checks_ready(checks)
    manifest = _write_manifest(root, config, checks, ready)
    outputs.append(manifest)

    if strict and not ready:
        raise ConfigError(f"High-quality preparation is incomplete; see {manifest}")

    return PreparationResult(outputs=outputs, manifest=manifest, ready=ready)


def _rewrite_configured_official_urls(config: EOCConfig) -> None:
    changed = False
    data = json.loads(config.path.read_text(encoding="utf-8"))
    for item in data.get("source_downloads", []):
        if not isinstance(item, dict):
            continue
        official = item.get("official_url")
        if official and _is_placeholder_url(item.get("url", "")):
            item["url"] = official
            changed = True
    if changed:
        config.path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


def _fail_on_required_placeholders(config: EOCConfig) -> None:
    for item in config.data.get("source_downloads", []):
        if not isinstance(item, dict):
            continue
        if item.get("required", True) and _is_placeholder_url(item.get("url", "")):
            raise ConfigError(
                f"Required source '{item.get('source_id')}' still uses a placeholder URL: {item.get('url')}"
            )


def _inspect_source_downloads(config: EOCConfig) -> list[dict[str, Any]]:
    checks = []
    for item in config.data.get("source_downloads", []):
        if not isinstance(item, dict):
            continue
        target = _resolved(config.relpath(item.get("target")))
        url = item.get("url", "")
        checks.append({
            "source_id": item.get("source_id"),
            "url": url,
            "target": str(target) if target else None,
            "required": bool(item.get("required", True)),
            "placeholder_url": _is_placeholder_url(url),
            "exists": bool(target and target.exists()),
            "status": _download_status(item, target),
        })
    return checks


def _inspect_freshness(config: EOCConfig) -> list[dict[str, Any]]:
    checks = []
    downloads_by_source = {
        item.get("source_id"): item
        for item in config.data.get("source_downloads", [])
        if isinstance(item, dict)
    }
    for source_id, source in config.data.get("sources", {}).items():
        if not isinstance(source, dict):
            continue
        freshness = source.get("freshness")
        if not isinstance(freshness, dict):
            continue
        item = downloads_by_source.get(source_id, {})
        target = _resolved(config.relpath(item.get("target"))) if item else None
        max_age = int(freshness.get("maximum_age_days", 0))
        age_days = _file_age_days(target) if target and target.exists() else None
        fresh = age_days is not None and (max_age <= 0 or age_days <= max_age)
        checks.append({
            "source_id": source_id,
            "target": str(target) if target else None,
            "maximum_age_days": max_age,
            "age_days": age_days,
            "fresh": fresh,
            "status": "fresh" if fresh else "missing_or_stale",
            "update_policy": freshness.get("update_policy"),
        })
    return checks


def _inspect_mpa_inputs(config: EOCConfig) -> dict[str, Any]:
    layer = config.layer("marine_protected_areas")
    if not layer.get("enabled", False):
        return {"enabled": False, "ready": True, "status": "disabled"}
    geometry = _resolved(config.relpath(layer.get("path")))
    rules = _resolved(config.relpath(layer.get("rules_path")))
    geometry_exists = bool(geometry and geometry.exists())
    rules_exists = bool(rules and rules.exists())
    ready = geometry_exists and rules_exists
    return {
        "enabled": True,
        "required": bool(layer.get("required", False)),
        "geometry_path": str(geometry) if geometry else None,
        "rules_path": str(rules) if rules else None,
        "geometry_exists": geometry_exists,
        "rules_exists": rules_exists,
        "ready": ready or not bool(layer.get("required", False)),
        "status": "ready" if ready else "omitted_or_incomplete",
    }


def _inspect_openbridge_symbols(config: EOCConfig) -> dict[str, Any]:
    symbols = config.data.get("symbols", {})
    library = symbols.get("libraries", {}).get("openbridge_icons", {})
    dictionary = symbols.get("dictionary", {})
    if not library:
        return {"configured": False, "ready": True, "symbols": []}
    root = _resolved(config.relpath(library.get("local_root")))
    entries = []
    ready = True
    for name, entry in dictionary.items():
        if not isinstance(entry, dict) or entry.get("library") != "openbridge_icons":
            continue
        asset = entry.get("asset")
        asset_path = root / asset if root and asset else None
        exists = bool(asset_path and asset_path.exists() and asset_path.suffix.lower() == ".svg")
        fallback_ok = entry.get("fallback_allowed") is False
        entry_ready = exists and fallback_ok
        ready = ready and entry_ready
        entries.append({
            "feature_class": name,
            "asset": str(asset_path) if asset_path else None,
            "exists": exists,
            "fallback_allowed": entry.get("fallback_allowed"),
            "ready": entry_ready,
        })
    return {
        "configured": True,
        "required": bool(library.get("required", False)),
        "source_url": library.get("source_url"),
        "license": library.get("license"),
        "local_root": str(root) if root else None,
        "ready": ready or not bool(library.get("required", False)),
        "symbols": entries,
    }


def _checks_ready(checks: dict[str, Any]) -> bool:
    for item in checks["source_downloads"]:
        if item["required"] and item["status"] not in {"available", "provider_configured"}:
            return False
    for item in checks["freshness"]:
        if item["status"] != "fresh":
            return False
    if not checks["marine_protected_areas"]["ready"]:
        return False
    if not checks["openbridge_symbols"]["ready"]:
        return False
    return True


def _write_manifest(root: Path, config: EOCConfig, checks: dict[str, Any], ready: bool) -> Path:
    path = root / "metadata" / "high_quality_preparation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "configuration_file": str(config.path),
        "ready_for_high_quality_run": ready,
        "synthetic_data_used": False,
        "checks": checks,
        "policy": "Only configured official/open source URLs and local SVG assets are used. Missing optional data is recorded; required missing data fails in strict mode.",
    }, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _download_status(item: dict[str, Any], target: Path | None) -> str:
    if _is_placeholder_url(item.get("url", "")):
        return "configuration_required"
    if item.get("provider"):
        return "available" if target and target.exists() else "provider_configured"
    if target and target.exists():
        return "available"
    if item.get("required", True):
        return "missing_required"
    return "optional_missing"


def _is_placeholder_url(url: str) -> bool:
    return any(marker in url for marker in PLACEHOLDER_MARKERS)


def _file_age_days(path: Path | None) -> float | None:
    if path is None or not path.exists():
        return None
    now = datetime.now(timezone.utc).timestamp()
    return (now - path.stat().st_mtime) / 86400


def _resolved(path: Path | None) -> Path | None:
    return path.resolve() if path is not None else None
