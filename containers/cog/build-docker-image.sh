#!/bin/bash


docker build \
    -t cuahsi/tif2cog:latest \
    -f Dockerfile.gdal_translate \
    .
