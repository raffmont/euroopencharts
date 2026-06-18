# Tutorial: ingest Marine Protected Areas

1. Download an official or openly licensed MPA dataset from the relevant authority.
2. Convert it to GeoJSON if needed.
3. Add mandatory geometry/provenance fields: `name`, `official_id`, `designation`, `status`, `managing_authority`, `legal_instrument`, `zone_id`, `zone_name`, `zone_type`, `source_name`, `source_url`, `license`, and `acquisition_timestamp`.
4. Create a rules JSON file from official legal text or authority data. Each zone/default rule must include permissions, prohibitions, anchoring, fishing, diving, transit, speed limits, mooring, temporal restrictions, and source reference.
5. Update `config.json` paths.
6. Run:

```bash
python run_actual_data_only.py --config config.json
```

If geometry exists but rules are missing and `fail_if_rules_missing_when_geometry_present` is true, the run fails. This prevents rule fabrication.

Do not infer missing restrictions from map appearance, local custom, or neighboring zones. If official rules are unavailable, mark the MPA layer optional and let the output manifest record the omission.
