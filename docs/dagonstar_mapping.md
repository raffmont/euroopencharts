# DAGonStar mapping

This prototype intentionally keeps task inputs and outputs explicit so the workflow can be transferred to DAGonStar.

| Prototype task | Future DAGonStar task |
| --- | --- |
| `validate_config` | single JSON configuration, OpenBridge symbol dictionary, source quality, and freshness validation |
| `fetch_copernicus` | containerized Copernicus/EMODnet acquisition |
| `fetch_gebco` | GEBCO AOI subset acquisition with TID/provenance metadata |
| `fetch_openseamap` | OSM/OpenSeaMap extraction and ODbL attribution |
| `validate_ports` | freshness and schema validation for harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons |
| `validate_mpa` | official MPA geometry, zones, permissions, prohibitions, and legal-rule validation |
| `validate_symbols` | OpenBridge SVG asset and license validation |
| `derive_bathymetry` | tiled bathymetry QC and contour generation |
| `derive_anchorages` | anchorage scoring from depth, shelter, seabed, and UGC |
| `metadata_stac` | FAIR metadata publication |
| `export_signalk` | Signal K resources export |
| `export_opencpn` | S-57/KAP/MBTiles/OpenCPN bundle export |
| `export_figure` | scientific figure generation |
| `zip_bundle` | offline release artifact |
