# Generated outputs

The legacy prototype example writes `data/example`, produced by running:

```bash
PYTHONPATH=src python -m euroopencharts.cli run-example --data-root data/example --workers 4
```

Key generated files:

- `data/example/raw/copernicus/bathymetry_grid.csv`
- `data/example/raw/openseamap/seamarks.geojson`
- `data/example/intermediate/derived/depth_contours.geojson`
- `data/example/intermediate/derived/anchorages.geojson`
- `data/example/intermediate/qc/bathymetry_qc.json`
- `data/example/metadata/stac_item.json`
- `data/example/offline_bundle/signalk/resources.json`
- `data/example/offline_bundle/opencpn/*.geojson`
- `data/example/figures/prototype_bathymetry_seamarks.svg`
- `data/example/dist/tyrrhenian-east-prototype-bundle.zip`

## Copyright-safe final chart rendering

The unattended pipeline now emits a final graphical chart rendering in:

- `figures/tyrrhenian_east_nautical_chart_render.png`
- `figures/tyrrhenian_east_nautical_chart_render.pdf`

The renderer is implemented in `euroopencharts.export.export_chart_rendering` and uses only project-owned Python drawing code plus generated data products. It does not copy proprietary map tiles, screenshots, icons, fonts, color palettes, or branded UI assets. Production symbol selection is controlled by the single JSON configuration file.

## High-quality actual-data outputs

The high-quality actual-data example writes under `data/highest_quality_map` unless `data_root` is changed in `examples/highest_quality_map_config.json`.

Expected output families:

- `figures/tyrrhenian_east_actual_data_chart.png`
- `figures/tyrrhenian_east_actual_data_chart.pdf`
- `metadata/source_downloads/*.json`
- `metadata/source_quality_requirements.json`
- `metadata/marine_protected_areas_provenance.json` or `metadata/marine_protected_areas_omitted.json`
- `offline_bundle/manifest.json`
- `offline_bundle/opencpn/*.geojson` when authoritative vector layers are available
- `dist/tyrrhenian-east-actual-data-only-bundle.zip`

The high-quality config requires OpenBridge Icons for applicable maritime symbols through `symbols.dictionary`. Assets must be local SVG files, and substitutions outside the dictionary are forbidden.

The output is still an experimental scientific prototype and is not for primary navigation.
