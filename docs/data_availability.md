# Data availability

The actual-data-only pipeline never fabricates missing information.

Default local sources:

- GSHHS coastline data from the installed Basemap data package.
- ETOPO1 shaded relief image from the installed Basemap data package.

External sources that must be supplied or downloaded as actual datasets:

- Copernicus Marine / EMODnet numeric bathymetry;
- OpenSeaMap/OpenStreetMap seamarks;
- official harbor and marina datasets;
- official Marine Protected Area geometry and zone/rule datasets;
- official restricted area and traffic management datasets.

When an optional layer is unavailable, the manifest records the omission. When a required layer is unavailable, the workflow fails.
