# Automated testing

EuroOpenCharts uses an unattended pytest suite as a project quality gate.

Run all tests from the repository root:

```bash
python -m pytest
```

Run concise output:

```bash
python -m pytest -q
```

The tests validate the engineering contract in `AGENTS.md`:

- all operational settings come from `config.json` or an explicitly supplied JSON file;
- required sources fail fast when missing;
- optional sources produce omission metadata instead of synthetic fallback data;
- Marine Protected Area features include provenance, license metadata, zones, permissions, and rules;
- production outputs report `synthetic_data_used=false`;
- offline bundles do not contain placeholder restricted-area layers or manually drawn chart-cell products;
- the documentation and AGENTS contract include the required testing and documentation rules.

Tests do not require internet access. Test fixtures are intentionally small, are used only inside temporary directories, and must never be shipped as production chart content.
