# OpenCPN and Signal K compatibility

The current prototype exports:

- OpenCPN supplemental GeoJSON layers under `offline_bundle/opencpn`.
- Signal K waypoint resources under `offline_bundle/signalk/resources.json`.

The high-quality actual-data workflow keeps OpenCPN/Signal K exports tied to validated source layers. Harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons must come from current configured extracts. Marine Protected Areas are exported only when official geometry and rules pass validation.

Production exporters should add:

- S-57 ENC where legally and technically feasible.
- KAP/BSB raster charts.
- MBTiles for offline tiled clients.
- GeoPackage for QGIS and scientific workflows.
- Optional S-100/S-101/S-102 research exporters.

OpenBridge symbols are configured for map rendering through the single JSON symbol dictionary. OpenCPN and Signal K data exports remain open data files; they should reference semantic feature classes rather than embedding raster icon substitutes.
