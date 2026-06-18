import json
from pathlib import Path

import pytest

from euroopencharts.config import ConfigError, load_config
from euroopencharts.mpa import process_mpa_layer


def _write_config(tmp_path: Path, *, required: bool, mpa_path: str | None, rules_path: str | None) -> Path:
    cfg = {
        "project": {
            "name": "EuroOpenCharts",
            "version": "test",
            "navigation_warning": "Experimental scientific prototype. Not for navigation.",
            "actual_data_only": True,
        },
        "data_root": "data/test-output",
        "area": {
            "id": "test-area",
            "name": "Test Area",
            "crs": "EPSG:4326",
            "west": 13.0,
            "south": 40.0,
            "east": 15.0,
            "north": 42.0,
        },
        "layers": {
            "marine_protected_areas": {
                "enabled": True,
                "required": required,
                "source_id": "test_mpa_source",
                "path": mpa_path,
                "rules_path": rules_path,
                "fail_if_rules_missing_when_geometry_present": True,
            }
        },
        "sources": {
            "test_mpa_source": {
                "name": "Test-only authoritative MPA fixture",
                "role": "unit test fixture",
                "license": "test fixture license",
                "actual_dataset": True,
                "test_fixture": True,
            }
        },
        "rendering": {"profile": "test"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def _valid_mpa_geojson(path: Path) -> None:
    data = {
        "type": "FeatureCollection",
        "test_fixture": True,
        "features": [
            {
                "type": "Feature",
                "id": "mpa-test-zone-a",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [14.0, 40.6], [14.1, 40.6], [14.1, 40.7], [14.0, 40.7], [14.0, 40.6]
                    ]],
                },
                "properties": {
                    "name": "Test MPA Zone A",
                    "zone_id": "A",
                    "source_name": "Test-only authoritative MPA fixture",
                    "source_url": "file://tests/fixtures/mpa.geojson",
                    "license": "test fixture license",
                    "test_fixture": True,
                },
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _valid_rules(path: Path) -> None:
    rules = {
        "test_fixture": True,
        "zones": {
            "A": {
                "zone_id": "A",
                "zone_name": "Strict protection test zone",
                "permissions": ["transit at safe speed"],
                "prohibitions": ["anchoring"],
                "anchoring": "prohibited",
                "fishing": "prohibited",
                "diving": "permit required",
                "transit": "allowed",
            }
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rules), encoding="utf-8")


def test_optional_missing_mpa_writes_omission_report(tmp_path: Path):
    cfg_path = _write_config(tmp_path, required=False, mpa_path="data/sources/missing.geojson", rules_path=None)
    config = load_config(cfg_path)
    outputs = process_mpa_layer(config, tmp_path / "out")
    omission = tmp_path / "out" / "metadata" / "marine_protected_areas_omitted.json"
    assert omission in outputs
    data = json.loads(omission.read_text(encoding="utf-8"))
    assert data["omitted"] is True
    assert data["synthetic_data_used"] is False


def test_required_missing_mpa_fails_fast(tmp_path: Path):
    cfg_path = _write_config(tmp_path, required=True, mpa_path="data/sources/missing.geojson", rules_path=None)
    config = load_config(cfg_path)
    with pytest.raises(ConfigError, match="not found"):
        process_mpa_layer(config, tmp_path / "out")


def test_mpa_geometry_requires_rules_when_configured(tmp_path: Path):
    mpa = tmp_path / "data/sources/mpa.geojson"
    _valid_mpa_geojson(mpa)
    cfg_path = _write_config(tmp_path, required=True, mpa_path="data/sources/mpa.geojson", rules_path="data/sources/missing_rules.json")
    config = load_config(cfg_path)
    with pytest.raises(ConfigError, match="rules file is missing"):
        process_mpa_layer(config, tmp_path / "out")


def test_valid_mpa_ingestion_adds_rules_and_provenance(tmp_path: Path):
    mpa = tmp_path / "data/sources/mpa.geojson"
    rules = tmp_path / "data/sources/rules.json"
    _valid_mpa_geojson(mpa)
    _valid_rules(rules)
    cfg_path = _write_config(tmp_path, required=True, mpa_path="data/sources/mpa.geojson", rules_path="data/sources/rules.json")
    config = load_config(cfg_path)
    process_mpa_layer(config, tmp_path / "out")

    out = tmp_path / "out" / "intermediate" / "derived" / "marine_protected_areas.geojson"
    prov = tmp_path / "out" / "metadata" / "marine_protected_areas_provenance.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    props = data["features"][0]["properties"]
    assert props["synthetic"] is False
    assert props["rules"]["anchoring"] == "prohibited"
    assert props["rules"]["transit"] == "allowed"
    assert json.loads(prov.read_text(encoding="utf-8"))["synthetic_data_used"] is False


def test_synthetic_mpa_feature_is_forbidden(tmp_path: Path):
    mpa = tmp_path / "data/sources/mpa.geojson"
    rules = tmp_path / "data/sources/rules.json"
    _valid_mpa_geojson(mpa)
    _valid_rules(rules)
    data = json.loads(mpa.read_text(encoding="utf-8"))
    data["features"][0]["properties"]["synthetic"] = True
    mpa.write_text(json.dumps(data), encoding="utf-8")
    cfg_path = _write_config(tmp_path, required=True, mpa_path="data/sources/mpa.geojson", rules_path="data/sources/rules.json")
    config = load_config(cfg_path)
    with pytest.raises(ConfigError, match="Synthetic MPA feature"):
        process_mpa_layer(config, tmp_path / "out")
