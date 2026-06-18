from pathlib import Path
from euroopencharts.workflow import run_example


def test_run_example(tmp_path: Path):
    result = run_example(tmp_path / "example", workers=2)
    assert "zip_bundle" in result
    assert (tmp_path / "example" / "offline_bundle" / "manifest.json").exists()
    assert (tmp_path / "example" / "figures" / "prototype_bathymetry_seamarks.svg").exists()
