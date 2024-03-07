
docker pull amazon/aws-cli:2.15.26 

source access-keys

docker run --rm -ti \
 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
 -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
 -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
 --entrypoint=/bin/bash \
amazon/aws-cli:2.15.26 
