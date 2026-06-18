# OpenCPN and Signal K compatibility

The current prototype exports:

- OpenCPN supplemental GeoJSON layers under `offline_bundle/opencpn`.
- Signal K waypoint resources under `offline_bundle/signalk/resources.json`.

Production exporters should add:

- S-57 ENC where legally and technically feasible.
- KAP/BSB raster charts.
- MBTiles for offline tiled clients.
- GeoPackage for QGIS and scientific workflows.
- Optional S-100/S-101/S-102 research exporters.
