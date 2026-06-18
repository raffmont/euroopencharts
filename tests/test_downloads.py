import json
from pathlib import Path

import pytest

from euroopencharts.config import load_config
from euroopencharts.downloads import download_configured_sources, validate_high_resolution_sources


def _config(tmp_path: Path, url: str, required: bool = True) -> Path:
    cfg = {
        "project": {
            "name": "EuroOpenCharts",
            "version": "test",
            "navigation_warning": "Experimental scientific prototype. Not for navigation.",
            "actual_data_only": True,
        },
        "data_root": "data/test-output",
        "area": {"id": "test", "name": "Test", "crs": "EPSG:4326", "west": 0, "south": 0, "east": 1, "north": 1},
        "layers": {},
        "sources": {
            "fixture_source": {
                "name": "Fixture source",
                "role": "download contract test",
                "license": "test fixture license",
                "actual_dataset": True,
                "quality": {
                    "resolution_class": "high",
                    "intended_use": "download contract test",
                    "feature_resolution": "test_fixture=true",
                    "nominal_scale": "test fixture",
                    "requires_current_extract": False,
                },
            }
        },
        "source_downloads": [{
            "source_id": "fixture_source",
            "url": url,
            "target": "data/test-sources/fixture.bin",
            "required": required,
            "skip_existing": False,
        }],
        "rendering": {"profile": "test"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_download_configured_sources_writes_manifest(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"actual fixture bytes")
    config = load_config(_config(tmp_path, source.as_uri()))
    outputs = download_configured_sources(config, tmp_path / "out")
    target = tmp_path / "data/test-sources/fixture.bin"
    manifest = tmp_path / "out/metadata/source_downloads/fixture_source.json"
    assert target in outputs
    assert manifest in outputs
    assert target.read_bytes() == b"actual fixture bytes"
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    assert metadata["status"] == "downloaded"
    assert metadata["source"]["license"] == "test fixture license"


def test_required_download_fails_fast(tmp_path: Path):
    missing = (tmp_path / "missing.bin").as_uri()
    config = load_config(_config(tmp_path, missing, required=True))
    with pytest.raises(RuntimeError, match="Required source download failed"):
        download_configured_sources(config, tmp_path / "out")


def test_optional_download_records_omission(tmp_path: Path):
    missing = (tmp_path / "missing.bin").as_uri()
    config = load_config(_config(tmp_path, missing, required=False))
    outputs = download_configured_sources(config, tmp_path / "out")
    manifest = tmp_path / "out/metadata/source_downloads/fixture_source.json"
    assert manifest in outputs
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    assert metadata["status"] == "omitted"


def test_high_resolution_sources_require_quality_metadata(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"actual fixture bytes")
    path = _config(tmp_path, source.as_uri())
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["sources"]["fixture_source"]["quality"]
    path.write_text(json.dumps(data), encoding="utf-8")
    config = load_config(path)
    with pytest.raises(Exception, match="quality block"):
        validate_high_resolution_sources(config, tmp_path / "out")


def test_current_extract_sources_require_freshness_metadata(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"actual fixture bytes")
    path = _config(tmp_path, source.as_uri())
    data = json.loads(path.read_text(encoding="utf-8"))
    data["sources"]["fixture_source"]["quality"]["requires_current_extract"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    config = load_config(path)
    with pytest.raises(Exception, match="freshness metadata"):
        validate_high_resolution_sources(config, tmp_path / "out")
