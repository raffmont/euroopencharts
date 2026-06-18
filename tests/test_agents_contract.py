from pathlib import Path


def test_agents_formalizes_automated_testing_and_openbridge():
    text = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "Automated testing and quality gates" in text
    assert "python -m pytest" in text
    assert "OpenBridge" in text
    assert "Single configuration file" in text
    assert "Documentation quality" in text


def test_testing_documentation_exists():
    text = Path("docs/testing.md").read_text(encoding="utf-8")
    assert "python -m pytest" in text
    assert "synthetic_data_used=false" in text
