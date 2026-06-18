# Generated output example

The delivered archive includes `data/example`, produced by running:

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

The renderer is implemented in `euroopencharts.export.export_chart_rendering` and uses only project-owned Python drawing code plus generated data products. It does not copy proprietary map tiles, screenshots, icons, fonts, color palettes, or branded UI assets. The style uses generic nautical-chart conventions: yellow land, white sea, gray contours, magenta cell frames, red dashed notices, simple harbor/light/buoy/anchorage symbols, depth labels, and a scale bar.

The output is still an experimental scientific prototype and is not for primary navigation.
