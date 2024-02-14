#!/bin/bash


docker run --rm -it \
    -p 8787:8787 \
    -v $(pwd)/domain:/srv/input/domain \
    -v $(pwd)/forcing:/srv/input/forcing \
    -v $(pwd)/cfe-out:/srv/output \
    --entrypoint=/bin/bash \
    cuahsi/cfe-configure:latest
#    /srv/input/domain/wb-2917533_upstream_subset.gpkg \
#    /srv/input/forcing/results.nc \
#    /srv/input/domain/cfe_noahowp_attributes.csv \
#    /srv/output \
#    1 \
#    7 \
#    --verbose



#docker run --rm \
#    -p 8787:8787 \
#    -v $(pwd)/input-data:/srv/input \
#    -v $(pwd)/output-data:/srv/output \
#    cuahsi/cfe-configure:latest \
#    /srv/input/wb-2917533_upstream_subset.gpkg \
#    /srv/input/results.nc \
#    /srv/input/cfe_noahowp_attributes.csv \
#    /srv/output \
#    1 \
#    7 \
#    --verbose
