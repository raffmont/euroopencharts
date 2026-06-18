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

## High-quality preparation command

The acquisition/preflight checklist is automated by:

```bash
euroopencharts prepare-high-quality --config path/to/config.json
```

The command reads only the supplied JSON config. It downloads configured `source_downloads`, writes source download and quality manifests, checks current-extract freshness, checks MPA geometry/rule file presence, validates OpenBridge local SVG assets, and writes `metadata/high_quality_preparation.json`.

The `overpass_seamarks` provider builds an AOI-bounded Overpass query from the configured `area` and writes a GeoJSON extract for OpenStreetMap/OpenSeaMap harbors, marinas, bays, anchorages, moorings, lights, buoys, beacons, and other `seamark:type` features. GEBCO, EMODnet, and official MPA datasets must still use official configured URLs or local authoritative files; the workflow does not guess them.

`--write-config` replaces placeholder `url` values only when the same entry already provides an explicit `official_url`. It does not guess official MPA sources or OpenBridge assets.

`--strict` fails when any required high-quality input is missing, stale, incomplete, or still configured with a placeholder URL.
