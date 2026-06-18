from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from urllib.error import URLError
from urllib.request import urlopen

from .config import EOCConfig, ConfigError


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
    if not _is_inside(target, config.path.parent) and not _is_inside(target, root):
        raise ConfigError(f"Download target must stay inside the project/config tree: {target}")

    required = bool(item.get("required", True))
    manifest_path = root / "metadata" / "source_downloads" / f"{source_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

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
