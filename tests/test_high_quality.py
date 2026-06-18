import json
from pathlib import Path

import pytest

from euroopencharts.config import ConfigError
from euroopencharts.high_quality import prepare_high_quality_run


def _write_config(tmp_path: Path, source_url: str) -> Path:
    source = tmp_path / "source.bin"
    source.write_bytes(b"official fixture bytes")
    icon_root = tmp_path / "resources/symbols/openbridge"
    icon_root.mkdir(parents=True)
    for icon in ["harbor.svg", "protected-area.svg"]:
        (icon_root / icon).write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" />", encoding="utf-8")
    mpa = tmp_path / "data/sources/highest_quality/mpa/marine_protected_areas.geojson"
    rules = tmp_path / "data/sources/highest_quality/mpa/marine_protected_area_rules.json"
    mpa.parent.mkdir(parents=True)
    mpa.write_text("{\"type\":\"FeatureCollection\",\"features\":[]}", encoding="utf-8")
    rules.write_text("{\"zones\":{}}", encoding="utf-8")
    cfg = {
        "project": {
            "name": "EuroOpenCharts",
            "version": "test",
            "navigation_warning": "Experimental scientific prototype. Not for navigation.",
            "actual_data_only": True,
        },
        "data_root": "data/out",
        "area": {"id": "test", "name": "Test", "crs": "EPSG:4326", "west": 0, "south": 0, "east": 1, "north": 1},
        "symbols": {
            "libraries": {
                "openbridge_icons": {
                    "name": "OpenBridge Icons",
                    "source_url": "https://www.openbridge.no/cases/openbridge-icons",
                    "license": "test OpenBridge license",
                    "type": "svg",
                    "local_root": "resources/symbols/openbridge",
                    "required": True,
                }
            },
            "dictionary": {
                "harbor": {"library": "openbridge_icons", "asset": "harbor.svg", "fallback_allowed": False},
                "marine_protected_area": {"library": "openbridge_icons", "asset": "protected-area.svg", "fallback_allowed": False},
            },
        },
        "layers": {
            "marine_protected_areas": {
                "enabled": True,
                "required": True,
                "source_id": "official_mpa_geojson",
                "path": "data/sources/highest_quality/mpa/marine_protected_areas.geojson",
                "rules_path": "data/sources/highest_quality/mpa/marine_protected_area_rules.json",
            },
            "harbors_marinas_bays": {
                "enabled": True,
                "required": True,
                "source_id": "openseamap_osm",
            },
        },
        "sources": {
            "openseamap_osm": {
                "name": "Fixture OSM extract",
                "role": "test",
                "license": "ODbL",
                "actual_dataset": True,
                "quality": {
                    "resolution_class": "high",
                    "intended_use": "test current extract",
                    "feature_resolution": "test fixture",
                    "requires_current_extract": True,
                },
                "freshness": {
                    "maximum_age_days": 30,
                    "acquired_at_field": "acquisition_timestamp",
                    "update_policy": "refresh test fixture",
                },
            },
            "official_mpa_geojson": {
                "name": "Fixture MPA",
                "role": "test",
                "license": "test license",
                "actual_dataset": True,
                "quality": {
                    "resolution_class": "high",
                    "intended_use": "test mpa",
                    "feature_resolution": "test fixture",
                },
            },
        },
        "source_downloads": [{
            "source_id": "openseamap_osm",
            "url": source_url,
            "target": "data/sources/highest_quality/seamarks/openseamap.osm.pbf",
            "required": True,
            "skip_existing": False,
        }],
        "rendering": {"profile": "test"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_prepare_high_quality_downloads_and_writes_ready_manifest(tmp_path: Path):
    source = tmp_path / "official.osm.pbf"
    source.write_bytes(b"official extract")
    config = _write_config(tmp_path, source.as_uri())
    result = prepare_high_quality_run(config, strict=True)
    manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert result.ready is True
    assert manifest["ready_for_high_quality_run"] is True
    assert manifest["checks"]["openbridge_symbols"]["ready"] is True


def test_prepare_high_quality_strict_rejects_placeholder_required_url(tmp_path: Path):
    config = _write_config(tmp_path, "https://example.invalid/replace-with-official.osm.pbf")
    with pytest.raises(ConfigError, match="placeholder URL"):
        prepare_high_quality_run(config, strict=True)


def test_prepare_high_quality_can_rewrite_configured_official_url(tmp_path: Path):
    source = tmp_path / "official.osm.pbf"
    source.write_bytes(b"official extract")
    config = _write_config(tmp_path, "https://example.invalid/replace-with-official.osm.pbf")
    data = json.loads(config.read_text(encoding="utf-8"))
    data["source_downloads"][0]["required"] = False
    data["source_downloads"][0]["official_url"] = source.as_uri()
    config.write_text(json.dumps(data), encoding="utf-8")
    result = prepare_high_quality_run(config, write_config=True)
    rewritten = json.loads(config.read_text(encoding="utf-8"))
    assert rewritten["source_downloads"][0]["url"] == source.as_uri()
    assert result.ready is True
