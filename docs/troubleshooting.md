# Troubleshooting

## Configuration file not found

Pass the path explicitly:

```bash
python run_actual_data_only.py --config config.json
```

## MPA source missing

If the layer is optional, the workflow writes `metadata/marine_protected_areas_omitted.json`.

If the layer is required, provide the source file or set `required` to false.

## MPA rules missing

When MPA geometry is present, rules must also be present if `fail_if_rules_missing_when_geometry_present` is true.

## Synthetic data detected

Production runs fail if an MPA feature contains `synthetic=true`.
