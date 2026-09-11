docker run --rm -ti \
  -v $(pwd)/api:/tmp/api \
  -v $(pwd)/.env:/tmp/.env \
  -v $(pwd)/debug.py:/tmp/debug.py \
  -w /tmp \
  --entrypoint=/bin/bash \
  cuahsi/metadata-extractor:latest \
  -c 'python debug.py'
