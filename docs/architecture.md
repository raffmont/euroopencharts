# Architecture

EuroOpenCharts is organized as a reproducible workflow:

```text
fetch -> normalize -> validate -> derive -> export -> package
```

The prototype uses a small local executor named `MiniDAGonStarExecutor`. The final implementation should map each task to DAGonStar jobs and containers.

## Data layers

- Gridded depth.
- Depth contours.
- Seafloor type placeholder layer in the data model.
- Lights and buoys.
- Harbors and marinas.
- Protected anchorages.
- Points of interest.
- User-generated content placeholders.

## Offline outputs

The workflow builds an offline bundle containing OpenCPN supplemental layers, Signal K resources, metadata, provenance, QC reports, and figures.

## Production replacement tasks

Replace the synthetic source tasks with:

- Copernicus Marine / EMODnet bathymetry downloads.
- OpenSeaMap / OSM Overpass or planet extract processing.
- Official open hydrographic and port authority datasets.
- Signal K crowdsourced sounding ingestion.
