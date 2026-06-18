# Marine Protected Areas

Marine Protected Areas are first-class layers.

Configure them in `config.json`:

```json
{
  "layers": {
    "marine_protected_areas": {
      "enabled": true,
      "required": false,
      "source_id": "official_mpa_geojson",
      "path": "data/sources/mpa/marine_protected_areas.geojson",
      "rules_path": "data/sources/mpa/marine_protected_area_rules.json",
      "render": true,
      "fail_if_rules_missing_when_geometry_present": true
    }
  }
}
```

## Geometry schema

The MPA geometry file must be GeoJSON `FeatureCollection` containing only `Polygon` or `MultiPolygon` features.

Required properties per feature:

```text
name
official_id
designation
status
managing_authority
legal_instrument
zone_id
zone_name
zone_type
source_name
source_url
license
acquisition_timestamp
```

Recommended properties:

```text
source_scale
processing_timestamp
confidence
```

## Rules schema

The rules file is JSON. It must contain either `zones` or `default_rules`.

Each rule entry must contain:

```text
zone_id
zone_name
permissions
prohibitions
anchoring
fishing
diving
transit
speed_limits
mooring
temporal_restrictions
source_reference
```

Example structure:

```json
{
  "zones": {
    "A": {
      "zone_id": "A",
      "zone_name": "Integral reserve",
      "permissions": [],
      "prohibitions": ["anchoring", "fishing"],
      "anchoring": "prohibited unless explicitly authorized",
      "fishing": "prohibited",
      "diving": "authorization required",
      "transit": "regulated",
      "speed_limits": "as specified by official regulation",
      "mooring": "prohibited unless explicitly authorized",
      "temporal_restrictions": "none",
      "source_reference": "official regulation URL or document identifier"
    }
  }
}
```

The example above documents the required shape only. Do not copy it into production unless it matches an actual official source.
