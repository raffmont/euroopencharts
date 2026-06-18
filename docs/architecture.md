# Architecture

EuroOpenCharts is organized as a reproducible workflow:

```text
fetch -> normalize -> validate -> derive -> export -> package
```

The prototype uses a small local executor named `MiniDAGonStarExecutor`. The final implementation should map each task to DAGonStar jobs and containers.

## Data layers

- Gridded depth.
- Depth contours.
- Seafloor coverage when supplied by authoritative high-resolution sources.
- Lights and buoys.
- Harbors, marinas, bays, ports, anchorages, and moorings from current authoritative/open vector extracts.
- Protected anchorages.
- Points of interest.
- Marine Protected Areas with official geometry, zones, permissions, prohibitions, and legal-rule metadata.
- Signal K or user-contributed content only when explicitly sourced, licensed, and marked with provenance.

## Offline outputs

The workflow builds an offline bundle containing OpenCPN supplemental layers, Signal K resources, metadata, provenance, QC reports, and figures.

## Production acquisition tasks

Actual-data production workflows should use:

- GEBCO, Copernicus Marine, and EMODnet bathymetry downloads.
- OpenSeaMap / OSM Overpass or planet extract processing.
- Official open hydrographic and port authority datasets.
- Signal K crowdsourced sounding ingestion.

## Symbol architecture

Production symbol selection is declarative. The single JSON configuration file defines `symbols.libraries` and `symbols.dictionary`. OpenBridge SVG icons are the preferred symbol source whenever applicable and legally permitted. Raster-only icons, proprietary chart symbols, and silent symbol substitutions are forbidden.
