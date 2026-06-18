# Getting started

This tutorial runs the actual-data-only pipeline unattended.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python run_actual_data_only.py --config config.json
```

The actual-data renderer uses Basemap GSHHS/ETOPO data. A fresh environment must install the project dependencies with `pip install -e .`; the high-quality example also requires `basemap-data-hires` for `resolution=h`.

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

## High-quality run

The high-quality run uses a dedicated single configuration file:

```bash
python examples/create_highest_quality_map.py --config examples/highest_quality_map_config.json
```

Before making this a production run, replace all placeholder `source_downloads` URLs with official AOI-specific source URLs. Download or configure:

- GEBCO and/or EMODnet high-resolution bathymetry;
- current OpenStreetMap/OpenSeaMap vector extracts for seamarks, harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons;
- authoritative MPA GeoJSON geometry and JSON legal-rule files;
- local OpenBridge SVG assets under `resources/symbols/openbridge/`.

The workflow records source download manifests, source quality metadata, OpenBridge symbol configuration, MPA provenance, and explicit omission reports for unavailable optional layers.
