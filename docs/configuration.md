# Configuration

EuroOpenCharts uses one JSON configuration file for all scripts and modules.

Default file:

```text
config.json
```

Override mechanisms:

```bash
python run_actual_data_only.py --config path/to/config.json
EUROOPENCHARTS_CONFIG=path/to/config.json python run_actual_data_only.py
```

The configuration controls:

- data root;
- area of interest;
- CRS;
- enabled layers;
- required/optional status;
- source paths;
- provenance metadata;
- output formats;
- rendering switches;
- execution backend and workers.
- source download URLs and targets;
- source quality and freshness metadata;
- symbol libraries and the semantic symbol dictionary, including OpenBridge SVG assets.

No operational script should hardcode these values.

## High-quality source metadata

Every source used by the high-quality example must declare a `quality` block. The workflow rejects enabled or downloadable sources that do not state a high-resolution class, intended use, and a measurable resolution or scale. Current vector extracts, such as OpenStreetMap/OpenSeaMap seamarks, must also declare `freshness` metadata.

Required quality fields:

```text
resolution_class
intended_use
grid_resolution_arc_seconds, pixel_resolution_arc_seconds, nominal_scale, or feature_resolution
```

Current extract sources additionally require:

```text
maximum_age_days
acquired_at_field
update_policy
```

## OpenBridge symbols

OpenBridge Icons are configured under `symbols.libraries.openbridge_icons` and mapped under `symbols.dictionary`. Production cartography must use local/offline SVG assets, must record the OpenBridge source URL and license metadata, and must not allow silent fallback symbols.

Example dictionary entry:

```json
{
  "harbor": {
    "library": "openbridge_icons",
    "asset": "harbor.svg",
    "fallback_allowed": false
  }
}
```
