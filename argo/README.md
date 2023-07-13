
# Argo Developer Setup

This document outlines the steps necessary for a minimal Argo configuration for local development.


## 1. Create Kubernetes Cluster


[K3d](https://k3d.io/v5.4.7/) is used to run Argo on a local kubernetes cluster locally.

The following resources are useful if you're looking for additional information
regarding cluster setup using K3d.  
  - [K3d Configuration
Instructions](https://surenraju.medium.com/setup-your-personal-kubernetes-cluster-with-k3s-and-k3d-7979976cde5)

  - [Argo Configuration
Instructions](https://surenraju.medium.com/setup-local-dev-environment-for-argo-workflows-with-k3s-and-k3d-9089964ebfdc)

#### 1.1 Install K3d via cURL

```
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

#### 1.2 Create the Local Cluster

```
k3d cluster create [mycluster] 
```

> Resources for nodes can be specified if desired using
>
>```
>k3d cluster create --agents-memory 8G [mycluster] 
>```

>A more advanced cluster may look like
>
>```
>k3d cluster create dev-cluster --port 8080:80@loadbalancer --port 8443:443@loadbalancer --api-port 6443 --servers 3 --agents 3
>```


NOTE: If you need to restart the cluster, issue the following commands:

```
k3d cluster stop [mycluster]

k3d cluster start [mycluster] --wait
```

#### 1.3 Verify the Cluster is Running

List clusters

```
k3d cluster list

NAME           SERVERS   AGENTS   LOADBALANCER
argo-cluster   1/1       0/0      true
```

List nodes

```
kubectl get nodes

NAME                STATUS   ROLES                  AGE   VERSION
k3d-argo-server-0   Ready    control-plane,master   21m   v1.25.6+k3s1
```

Show underlying containers

```
docker ps

CONTAINER ID   IMAGE                            COMMAND                  CREATED         STATUS         PORTS                             NAMES
834f9c1e9696   ghcr.io/k3d-io/k3d-tools:5.4.7   "/app/k3d-tools noop"    3 minutes ago   Up 3 minutes                                     k3d-argo-cluster-tools
cae1065512e4   ghcr.io/k3d-io/k3d-proxy:5.4.7   "/bin/sh -c nginx-pr…"   3 minutes ago   Up 3 minutes   80/tcp, 0.0.0.0:50096->6443/tcp   k3d-argo-cluster-serverlb
f9406384e40b   rancher/k3s:v1.25.6-k3s1         "/bin/k3d-entrypoint…"   3 minutes ago   Up 3 minutes                                     k3d-argo-cluster-server-0
```

## 2. Install Argo in the Cluster

For additional information regarding this process, see [Argo QuickStart](https://argoproj.github.io/argo-workflows/quick-start/)

The cluster can be installed via the `setup-argo.sh` script.

```
./setup-argo.sh
```

#### Additional Information

The following is a short explaination of the operations performed by the `setup-argo.sh` script.

Create Argo namespace

```
kubectl create namespace argo
```

Install Argo, get the version from: https://github.com/argoproj/argo-workflows/releases

```
ARGO_VERSION=3.4.8

kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v$ARGO_VERSION/install.yaml
```

Create a cluster role with elevated permissions and set it to the default. This is only for local development.

- https://argoproj.github.io/argo-workflows/service-accounts/#roles-role-bindings-and-service-accounts 
- https://argoproj.github.io/argo-workflows/workflow-rbac/ 

This may or may not be necessary since argo comes with several service accounts:

```
kubectl get serviceaccounts -n argo
NAME          SECRETS   AGE
default       0         4m49s
argo          0         4m48s
argo-server   0         4m48s

```

Submitting with `argo` should solve most problems, if not create an admin role as shown below.

```
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=argo:default -n argo
```

Submitting a job 

```
argo submit -n argo gcp-output-artifact-example.yaml
```

or 

```
argo submit -n argo --serviceaccount argo gcp-output-artifact-example.yaml
```

Patch Access and Control for Local Dev

```
kubectl patch deployment \
  argo-server \
  --namespace argo \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
  "server",
  "--auth-mode=server"
]}]'

```

Configure GCP Artifact Repository

```
kubectl apply artifact-repo-config.yaml -n argo
```

Launch Argo GUI

```
kubectl -n argo port-forward deployment/argo-server 2746:2746
```

