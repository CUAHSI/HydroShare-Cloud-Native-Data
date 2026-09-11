# Repository Context: HydroShare-Cloud-Native-Data

This file provides background context for AI assistants (Copilot CLI, chat agents,
etc.) working in this repository. It summarizes purpose, structure, conventions,
and key technologies so a new session can get oriented quickly without re-reading
the entire tree.

## Purpose

Exploration of **cloud-native data storage and processing patterns for HydroShare**
(CUAHSI's water data repository). The work has two main threads:

1. **Cloud-native metadata schema design** — extending HydroShare's resource data
   model to work with distributed, cloud-hosted data by writing Schema.org-based
   JSON-LD metadata files alongside content, rather than relying on a relational
   database. This supports FAIR data principles and interoperability with tools
   like Google Dataset Search.
2. **Cloud-native scientific workflows** — running hydrologic models (NextGen/ngen,
   CFE, ParFlow, NWM) and geospatial data-processing tasks (COG conversion,
   FlatGeobuf, kerchunk, metadata extraction) as containerized steps orchestrated
   with **Argo Workflows** on Kubernetes (GKE), producing cloud-optimized artifacts.

## Top-Level Layout

- `argo/` — Argo Workflows dev setup docs/scripts (K3d local cluster, GCP artifact
  repo config, `setup-argo.sh`).
- `containers/` — Dockerized components used as workflow steps:
  - `cfe/` — Conceptual Functional Equivalent (CFE) hydrologic model container,
    with `ngen-cal` and `t-route` as git submodules under `deps/`.
  - `cog/`, `gdal_translate/` — Cloud-Optimized GeoTIFF conversion via GDAL.
  - `fim/` — Flood Inundation Mapping utilities.
  - `forcing/aorc-v1.0`, `forcing/aorc-v1.1` — AORC forcing data processing.
  - `kerchunk/` — Kerchunk-based virtual Zarr dataset generation.
  - `metadata/user-metadata-extraction/` — FastAPI service (`api/`) + scripts to
    extract/merge HydroShare resource + file metadata into JSON-LD.
  - `nwm-v1/-v2/-v3-static-input/` — National Water Model static domain subsetting.
  - `parflow-v1/` — ParFlow model container.
- `workflows/` — Argo Workflow YAML definitions (one directory per workflow family):
  `aorc/`, `basic/`, `cloud-artifacts/`, `cog/`, `flatgeobuf/`, `metadata-extractor/`,
  `ngen/` (hydrofabric-subset, configure-cfe, run-cfe-complete, run-ngen), `parflow/`.
- `schema/` — Python package + docs defining the Schema.org-based metadata model:
  - `doc/` — Narrative docs: `core.md` (Core/Dataset/Vector/Raster/etc. hierarchy),
    `dataset.md` (Dataset-specific properties), `crosswalks.xlsx`, `best-practices/`.
  - `src/` — Pydantic models (`base.py`, `core.py`, `dataset.py`, `datavariable.py`),
    generated `schema_models/` (large auto-generated Schema.org class library),
    `json_schemas/`, `generate_jsonld.py`, `tests/`.
- `notebooks/` — Jupyter notebooks demonstrating COG/FlatGeobuf preview, ngen/ParFlow
  subsetting, and submitting Argo workflows from Python.
- `workshops/2024-ciroh/` — CIROH workshop materials/demos (slides + two demo
  notebooks running CFE in the cloud).

## Key Technologies

- **Kubernetes / GKE** (project `apps-320517`, cluster `hydroshare-workflows`) +
  **Argo Workflows** for orchestration; **K3d** for local dev clusters.
- **Docker** for all workflow step containers.
- **Python** (Pydantic models, FastAPI metadata service, Jupyter notebooks).
- **Schema.org / JSON-LD** as the metadata vocabulary; HydroShare's Dublin Core +
  `hsterms` extension informs the domain vocabulary.
- **GDAL, Kerchunk, FlatGeobuf** for cloud-optimized geospatial data formats.
- Hydrologic models: **NextGen (ngen)**, **CFE**, **t-route**, **ParFlow**, **NWM**.

## Conventions / Notes

- Argo jobs are typically submitted via
  `argo submit -n argo --serviceaccount argo <workflow>.yaml`, optionally with
  `-p key=value` overrides.
- Git submodules: `containers/cfe/deps/neg-cal` (ngen-cal) and
  `containers/cfe/deps/t-route`, both from NOAA-OWP.
- The repo contains many working/scratch artifacts (`.ipynb_checkpoints`,
  `__pycache__`, sample outputs like `*.tif`, `.zip`, `output/` dirs) left in
  place from exploratory work — treat these as non-authoritative build output,
  not source of truth.
- `schema/src/schema_models/` is a large auto-generated library mirroring
  Schema.org classes; prefer editing `schema/src/{base,core,dataset,datavariable}.py`
  for domain-specific model changes.
- Documentation for the metadata schema lives in `schema/doc/*.md`; keep these in
  sync with `schema/src/*.py` when metadata property changes are made.

## Where to Look First

| Task | Start here |
|---|---|
| Understand metadata schema design | `schema/doc/core.md`, `schema/doc/dataset.md` |
| Add/modify a metadata model class | `schema/src/core.py`, `dataset.py`, `datavariable.py`, `base.py` |
| Add/modify an Argo workflow | `workflows/<family>/*.yaml`, mirroring existing patterns |
| Add/modify a containerized step | `containers/<name>/Dockerfile` + `entry.py`/`build.sh` |
| Local Argo/K8s dev setup | `argo/README.md`, `argo/setup-argo.sh` |
| CFE/ngen model container | `containers/cfe/` (submodules in `deps/`) |
