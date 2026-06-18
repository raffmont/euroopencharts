# Getting started

This tutorial runs the actual-data-only pipeline unattended.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python run_actual_data_only.py --config config.json
```

Outputs are written under the `data_root` declared in `config.json`.

Default outputs:

```text
data/actual_data_only/figures/tyrrhenian_east_actual_data_chart.png
data/actual_data_only/figures/tyrrhenian_east_actual_data_chart.pdf
data/actual_data_only/metadata/actual_data_provenance.json
data/actual_data_only/metadata/marine_protected_areas_omitted.json
data/actual_data_only/offline_bundle/manifest.json
data/actual_data_only/dist/tyrrhenian-east-actual-data-only-bundle.zip
```

The default configuration uses actual local coastline/relief data available through the installed Basemap data package. It does not generate synthetic seamarks, depths, marine protected areas, or rules.
