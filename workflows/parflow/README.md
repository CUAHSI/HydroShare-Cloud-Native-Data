Use the following command to test this workflow locally:

```
argo submit -n argo --serviceaccount argo parflow-subset.yaml
```

The default job parameters can be overridden using the following syntax:

```
$ argo submit -n argo --serviceaccount argo parflow-subset.yaml -p job-id="q1w2e3r4t5y6u7i8o9p0" -p label="test"

Name:                parflow-subset-v1-82qjx
Namespace:           argo
ServiceAccount:      argo
Status:              Pending
Created:             Thu Jul 13 15:15:36 -0400 (now)
Progress:
Parameters:
  job-id:            q1w2e3r4t5y6u7i8o9p0
  label:             test
  pfinput:           /srv/input
  shape:             /srv/output/watershed.shp
  output:            /srv/output
```
