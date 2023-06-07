#!/bin/bash


docker run --rm -ti \
    -v $(pwd)/test-data:/tmp/test-data \
    cuahsi/kerchunk:latest \
    /bin/bash
