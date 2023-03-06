#!/bin/bash


docker run --rm -ti \
    -v /Users/castro/Documents/work/ciroh/cloud-data-conversion-fihm/sample-data:/tmp \
    tif2cog:latest \
    "-i" "/tmp/hydrodem_03N_03b.tif" "-o" "/tmp/hydrodem_03N_03b.cog"
