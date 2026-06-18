import json
from pathlib import Path

import pytest

from euroopencharts.config import ConfigError, load_config


def _minimal_config(tmp_path: Path) -> Path:
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
        "layers": {},
        "sources": {},
        "rendering": {"profile": "test"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_load_config_uses_single_json_file(tmp_path: Path):
    path = _minimal_config(tmp_path)
    config = load_config(path)
    assert config.path == path.resolve()
    assert config.data_root == path.parent / "data/test-output"
    assert config.area["crs"] == "EPSG:4326"


def test_load_config_fails_when_actual_data_only_is_false(tmp_path: Path):
    path = _minimal_config(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["project"]["actual_data_only"] = False
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="actual_data_only"):
        load_config(path)


def test_load_config_requires_area_crs(tmp_path: Path):
    path = _minimal_config(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["area"]["crs"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="area.crs"):
        load_config(path)
