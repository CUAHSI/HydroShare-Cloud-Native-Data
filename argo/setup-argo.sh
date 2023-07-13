#!/bin/bash

# This script will delete the Argo namespace and reinstall it

kubectl delete namespace argo

kubectl create namespace argo


ARGO_VERSION=3.4.8 
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v$ARGO_VERSION/install.yaml

kubectl patch deployment   argo-server   --namespace argo   --type='json'   -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
  "server",
  "--auth-mode=server"
]}]'

kubectl -n argo create secret generic my-gcs-creds --from-file=serviceAccountKey=gcp-service-acct-creds.json
