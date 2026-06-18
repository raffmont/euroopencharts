# AGENTS.md

## EuroOpenCharts engineering contract

EuroOpenCharts is a FAIR-compliant, offline-first, HPC/cloud-ready, DAGonStar-orchestrated Python framework for producing nautical chart and scientific geospatial data bundles for European inland and open waters, with the operational pilot set to the eastern Central-Southern Tyrrhenian Sea.

This file is normative. All agents, contributors, scripts, workflow tasks, tests, examples, and documentation must obey these rules.

## 1. Non-negotiable data constraints

The project SHALL NOT fabricate, approximate, hallucinate, or draw placeholder nautical data.

The project SHALL NOT add scaffolding in place of working behavior. Contributions must implement real working code, real validation, real acquisition/preparation logic, or real documentation that matches executable behavior.

The project SHALL NOT add placeholder components in operational paths. Components, commands, examples, workflows, and configured providers must be real active components, or they must fail/omit explicitly with provenance and a clear reason.

Forbidden in production outputs:

- synthetic bathymetry;
- synthetic depth contours;
- synthetic coastlines;
- synthetic seabed classes;
- synthetic lights, buoys, beacons, harbors, marinas, anchorages, POIs;
- synthetic marine protected areas;
- synthetic MPA zones, permissions, rules, or labels;
- synthetic restricted areas, traffic separation schemes, military areas, or chart cells;
- manually drawn regulatory polygons;
- silent fallback layers.

If a required source is unavailable, the workflow MUST fail fast with a clear error message. If an optional source is unavailable, the workflow MAY continue only when the output manifest explicitly records that the layer is omitted and why.

Synthetic or fixture data is allowed only inside automated tests and examples that are clearly marked `test_fixture=true` or `synthetic=true`, stored outside release bundles, and never published as scientific or navigational output.

## 2. Single configuration file constraint

All scripts, modules, examples, tests, and command-line entry points MUST read runtime settings from one JSON configuration file.

Default path:

```text
config.json
```

Alternative path MAY be passed explicitly with `--config` or the environment variable `EUROOPENCHARTS_CONFIG`.

No script may hardcode operational source paths, area bounds, output paths, layer enablement, quality thresholds, backend selection, or rendering switches outside this configuration file.

The configuration file is the single source of truth for:

- area of interest;
- CRS;
- data root;
- enabled layers;
- required versus optional sources;
- local source file paths;
- online source URLs/API endpoints;
- license/provenance metadata;
- rendering style profile;
- DAGonStar/HPC/cloud backend parameters;
- output formats;
- QC thresholds;
- symbol libraries, including OpenBridge assets.

## 3. FAIR principle enforcement

Every product SHALL be Findable, Accessible, Interoperable, and Reusable.

Findable:

- STAC metadata;
- stable identifiers;
- spatial/temporal indexes;
- searchable provenance records.

Accessible:

- offline bundles;
- documented file layout;
- documented API/export structure.

Interoperable:

- GeoPackage, GeoJSON, FlatGeobuf where applicable;
- GeoTIFF/COG, NetCDF, Zarr where applicable;
- Parquet/CSV for tables;
- S-57/KAP/MBTiles/OpenCPN-compatible export targets where legally and technically possible;
- Signal K resources/deltas where applicable;
- standards-aligned CRS and metadata.

Reusable:

- license metadata;
- source provenance;
- processing provenance;
- QC metrics;
- citation metadata;
- reproducible workflow/version information.

No data object may be released without source/provenance/license metadata.

## 4. Marine Protected Areas requirement

Marine Protected Areas are first-class data products.

The dataset model SHALL include:

- MPA polygon/multipolygon geometry;
- MPA name;
- official identifier when available;
- designation/status;
- managing authority;
- legal instrument or source reference;
- zone identifier and zone name;
- zone type/classification;
- permissions and prohibitions;
- anchoring rules;
- fishing rules;
- diving rules;
- transit/navigation rules;
- speed limits where applicable;
- mooring rules where applicable;
- temporal restrictions where applicable;
- source URL/path;
- license;
- acquisition timestamp;
- processing timestamp;
- confidence/QC status.

MPA zones, permissions, and rules SHALL only be rendered if sourced from official or openly licensed authoritative data. If geometry is present but rules are not available, the layer MUST state that rules are unavailable rather than inventing them.

## 5. Rendering and copyright constraint

Rendering SHALL use project-owned code and generic nautical/cartographic conventions. It SHALL NOT copy proprietary chart tiles, screenshots, icons, branded UI elements, color palettes, fonts, trade dress, or presentation libraries from commercial products.

Acceptable references:

- IHO S-52 concepts;
- OpenCPN-compatible conventions;
- OpenSeaMap/OSM-compatible open symbology;
- project-owned original symbols.

## 6. OpenBridge symbology constraint

The project SHALL use OpenBridge Design System symbols and icons whenever applicable and legally permitted by the OpenBridge license.

Symbol priority:

1. IHO/S-52 concepts where an official charting convention is required;
2. OpenBridge symbols/icons for maritime HMI consistency;
3. OpenSeaMap/OpenStreetMap symbols when data-source semantics are OSM/SeaMark based;
4. project-owned custom SVG symbols only when no standard/open symbol exists.

All symbols SHALL be local/offline assets with license metadata. Raster-only symbols are prohibited for production cartography; symbols MUST be available as SVG or another vector format suitable for PDF/SVG/print exports. Proprietary Navionics, Garmin, C-MAP, or other commercial chart symbols are forbidden.

A single symbol dictionary configured in `config.json` SHALL map semantic feature classes to icon assets. Symbol substitutions outside this dictionary are forbidden.

## 7. DAGonStar/HPC/cloud constraint

The final implementation SHALL be DAGonStar-native.

Every workflow stage SHALL be task-oriented with explicit:

- inputs;
- outputs;
- dependencies;
- resource requirements;
- provenance;
- QC gates;
- deterministic behavior.

The implementation SHALL run effectively on:

- local workstation;
- on-premises HPC cluster;
- Kubernetes;
- cloud batch;
- hybrid HPC/cloud infrastructure.

Stages SHALL support parallel and distributed execution, checkpointing, caching, resume, and tile/area partitioning.

## 8. Intermediate and final product constraint

All intermediate and final products SHALL be inspectable in QGIS and readable by Python scripts.

Every stage MUST prefer open, documented formats. Hidden binary-only intermediate products are forbidden.

## 9. Documentation quality constraint

The repository MUST contain high-quality, rock-solid, internally consistent documentation. Documentation is a deliverable, not an afterthought.

Required documentation under `docs/`:

- step-by-step getting started tutorial;
- installation and configuration guide;
- architecture overview;
- data flow description;
- data availability and source acquisition guide;
- marine protected areas guide;
- DAGonStar workflow mapping;
- HPC/cloud execution guide;
- OpenCPN and Signal K interoperability guide;
- QGIS and Python visualization guide;
- troubleshooting guide;
- reproducibility and FAIR compliance guide;
- automated testing guide.

Documentation MUST stay synchronized with the code and configuration schema. Every tutorial command MUST be runnable unattended. Every documented output path MUST match the actual project outputs. Examples MUST be minimal, tested, and deterministic.

## 10. Automated testing and quality gates

Automated unit, integration, contract, and smoke tests are mandatory. Pull requests and release candidates SHALL NOT be accepted unless the full test suite passes unattended.

Required test categories:

- configuration schema and single-configuration-file behavior;
- fail-fast behavior for missing required sources;
- optional source omission reports;
- MPA geometry, metadata, zone, permission, and rule validation;
- prohibition of synthetic data in production outputs;
- provenance and license metadata presence;
- output manifest consistency;
- offline bundle completeness;
- documentation path/command consistency where practical;
- rendering safety: no placeholder regulatory polygons, chart cells, or proprietary symbols;
- OpenBridge symbol configuration validation when symbols are enabled.

Testing rules:

- tests MUST run with `python -m pytest`;
- tests MUST be unattended and deterministic;
- tests MUST NOT require internet access;
- tests MUST write only to temporary directories or `data/test*` paths ignored by git;
- tests MAY use small fixtures, but fixtures MUST be labelled as test fixtures and MUST never be included in production bundles;
- tests MUST assert that production outputs contain `synthetic_data_used=false`;
- tests MUST fail when required provenance, license, or CRS fields are missing.

Recommended commands:

```bash
python -m pytest
python -m pytest -q
```

## 11. Failure policy

The workflow SHALL fail if:

- required source file is missing;
- required source download fails;
- provenance is missing;
- license metadata is missing;
- CRS is undefined;
- source layer schema is invalid;
- MPA zones/rules are requested but unavailable;
- QC threshold is violated;
- a task attempts to emit production data marked synthetic;
- tests fail.

Silent fallback behavior is forbidden.

## 12. Navigation warning

All prototype outputs MUST prominently include:

```text
Experimental scientific prototype. Not for navigation.
```
