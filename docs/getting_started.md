# Getting started

This tutorial runs the actual-data-only pipeline unattended.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python run_actual_data_only.py --config config.json
```

The source acquisition and preflight commands do not require Basemap. The graphical actual-data renderer uses Basemap GSHHS/ETOPO data; install renderer extras with `python -m pip install -e ".[figures]"` on a Python version supported by Basemap. Always use `python -m pip`, not bare `pip`, so packages install into the interpreter that will run the command. If your Python is newer than Basemap supports, run `prepare-high-quality` on that environment and render from a compatible environment.

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
euroopencharts prepare-high-quality --config examples/highest_quality_map_config.json
python examples/create_highest_quality_map.py --config examples/highest_quality_map_config.json
```

Before making this a production run, replace all placeholder `source_downloads` URLs with official AOI-specific source URLs. Download or configure:

- GEBCO and/or EMODnet high-resolution bathymetry;
- current OpenStreetMap/OpenSeaMap vector extracts for seamarks, harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons;
- authoritative MPA GeoJSON geometry and JSON legal-rule files;
- local OpenBridge SVG assets under `resources/symbols/openbridge/`.

The workflow records source download manifests, source quality metadata, OpenBridge symbol configuration, MPA provenance, and explicit omission reports for unavailable optional layers.

For production gates, run preparation with:

```bash
euroopencharts prepare-high-quality --config examples/highest_quality_map_config.json --strict
```

The strict mode fails when required configured downloads still use placeholder URLs, current OSM/OpenSeaMap extracts are stale or missing, MPA geometry/rules are incomplete, or required OpenBridge SVG assets are absent.
