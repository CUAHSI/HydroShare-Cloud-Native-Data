#!/bin/bash

/dmod/bin/ngen-serial \
	/ngen/data/domain/catchments.geojson all \
	/ngen/data/domain/nexus.geojson all \
	/ngen/data/config/realization.json
