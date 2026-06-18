# Data availability

The actual-data-only pipeline never fabricates missing information.

Default local sources:

- GSHHS coastline data from the installed Basemap data package.
- ETOPO1 shaded relief image from the installed Basemap data package.

External sources that must be supplied or downloaded as actual datasets:

- GEBCO and/or EMODnet numeric bathymetry at the highest available AOI resolution;
- OpenSeaMap/OpenStreetMap seamarks, ports, harbors, marinas, bays, anchorages, moorings, lights, buoys, and beacons from a current unsimplified vector extract;
- official harbor, marina, bay, port authority, and nautical services datasets where available;
- official Marine Protected Area geometry and zone/rule datasets;
- official restricted area and traffic management datasets.

When an optional layer is unavailable, the manifest records the omission. When a required layer is unavailable, the workflow fails.

## High-resolution example sources

`examples/highest_quality_map_config.json` declares quality expectations for:

- GEBCO gridded bathymetry, currently represented as a 15 arc-second global grid class;
- EMODnet Bathymetry regional products, configured as the preferred European high-resolution bathymetry source where available;
- GSHHS high-resolution coastline rendering;
- ETOPO1 one-arc-minute shaded relief, used only as a background and not as authoritative numeric bathymetry;
- current OpenStreetMap/OpenSeaMap vector features, downloaded through the configured Overpass AOI query, with a maximum age of 30 days for harbors, marinas, bays, seamarks, and related nautical features;
- official MPA geometry and legal-rule files, refreshed or verified against the official authority before production.

The example keeps external downloads optional until real official URLs, provenance, license, CRS, and redistribution terms are configured. Set sources to required only after those fields are complete.
