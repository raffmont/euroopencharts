import json
import zipfile
from pathlib import Path

from euroopencharts.actual_pipeline import _write_manifest, _zip_bundle
from euroopencharts.config import load_config


def _config(tmp_path: Path) -> Path:
    cfg = {
        "project": {
            "name": "EuroOpenCharts",
            "version": "test",
            "navigation_warning": "Experimental scientific prototype. Not for navigation.",
            "actual_data_only": True,
        },
        "data_root": "data/test-output",
        "area": {"id": "test", "name": "Test", "crs": "EPSG:4326", "west": 0, "south": 0, "east": 1, "north": 1},
        "layers": {"marine_protected_areas": {"enabled": True, "required": False}},
        "sources": {},
        "rendering": {"profile": "test"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_manifest_reports_actual_data_only_and_mpa_availability(tmp_path: Path):
    config = load_config(_config(tmp_path))
    root = tmp_path / "out"
    (root / "intermediate/derived").mkdir(parents=True)
    (root / "intermediate/derived/marine_protected_areas.geojson").write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    manifest_path = _write_manifest(root, config)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["synthetic_data_used"] is False
    assert manifest["marine_protected_areas"]["available"] is True
    assert manifest["warning"] == "Experimental scientific prototype. Not for navigation."


def test_bundle_excludes_placeholder_regulatory_layers(tmp_path: Path):
    config = load_config(_config(tmp_path))
    root = tmp_path / "out"
    (root / "metadata").mkdir(parents=True)
    (root / "metadata/actual_data_provenance.json").write_text('{"synthetic_data_used": false}', encoding="utf-8")
    _write_manifest(root, config)
    bundle = _zip_bundle(root)
    with zipfile.ZipFile(bundle) as z:
        names = set(z.namelist())
    forbidden = {
        "restricted_areas.geojson",
        "traffic_management.geojson",
        "chart_cell_boundaries.geojson",
        "manual_placeholder_polygons.geojson",
    }
    assert not any(name.endswith(tuple(forbidden)) for name in names)
