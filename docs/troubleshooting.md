# Troubleshooting

## Configuration file not found

Pass the path explicitly:

```bash
python run_actual_data_only.py --config config.json
```

## Basemap is missing

The actual-data renderer requires `basemap` and `basemap-data-hires` for GSHHS coastline and ETOPO rendering. These packages are optional because Basemap does not publish wheels for every Python release. In a compatible active virtual environment, run:

```bash
python -m pip install -e ".[figures]"
```

Use `python -m pip show basemap basemap-data-hires matplotlib` to verify packages are installed into the same interpreter reported by `python --version`. If bare `pip show` reports a different `.venv/lib/pythonX.Y` path than `python --version`, recreate the virtual environment or use `python -m pip` consistently. If pip reports that no Basemap version matches your Python version, keep using that environment for `euroopencharts prepare-high-quality`, and use a Basemap-compatible Python environment for rendering.

## MPA source missing

If the layer is optional, the workflow writes `metadata/marine_protected_areas_omitted.json`.

If the layer is required, provide the source file or set `required` to false.

## MPA rules missing

When MPA geometry is present, rules must also be present if `fail_if_rules_missing_when_geometry_present` is true.

## Synthetic data detected

Production runs fail if an MPA feature contains `synthetic=true`.

## OpenBridge symbol validation fails

When `symbols.libraries.openbridge_icons` is configured, every OpenBridge dictionary entry must reference a local `.svg` asset and must set `fallback_allowed` to `false`. Export the OpenBridge Icons to `resources/symbols/openbridge/`, record the license metadata in the config, and update `symbols.dictionary` if asset names differ.

## Harbor, marina, or bay extract is stale

The high-quality example requires current OpenStreetMap/OpenSeaMap extracts for harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons. Refresh the extract when it is older than the configured `maximum_age_days`, or leave the layer optional so the manifest records an omission.
