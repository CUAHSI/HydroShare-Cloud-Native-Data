#!/bin/bash


docker build \
    -t cuahsi/gdal_translate:latest \
    -f Dockerfile.gdal_translate \
    .
