# HPC and cloud execution model

The final implementation should execute each workflow stage through DAGonStar on:

- local workstations;
- on-premises HPC clusters;
- Kubernetes clusters;
- cloud batch systems;
- hybrid HPC/cloud deployments.

Every production task should accept:

```text
--area
--tile
--crs
--resolution
--workers
--backend local|hpc|kubernetes|cloud
--cache
--resume
```

Recommended production technologies:

- Dask or Ray for Python-level parallelism.
- MPI or job arrays for HPC tiling.
- GDAL/OGR and PROJ for geospatial transformations.
- PostGIS, GeoPackage, GeoParquet, and object storage.
- Docker/Podman for development and Apptainer/Singularity for HPC.
