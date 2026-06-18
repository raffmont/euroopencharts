# Tutorial: ingest Marine Protected Areas

1. Download an official or openly licensed MPA dataset from the relevant authority.
2. Convert it to GeoJSON if needed.
3. Add mandatory provenance fields: `name`, `source_name`, `source_url`, `license`.
4. Create a rules JSON file with official zone permissions and prohibitions.
5. Update `config.json` paths.
6. Run:

```bash
python run_actual_data_only.py --config config.json
```

If geometry exists but rules are missing and `fail_if_rules_missing_when_geometry_present` is true, the run fails. This prevents rule fabrication.
