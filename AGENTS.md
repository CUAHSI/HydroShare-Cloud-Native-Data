# AGENTS.md

Guidance for AI coding agents working in this repository.

## Start Here

Before making changes, read [`.ai/context.md`](.ai/context.md). It summarizes the
repository's purpose, top-level layout, key technologies, conventions, and a
"where to look first" table for common tasks (schema changes, Argo workflows,
containerized steps, local dev setup, etc.).

Keep `.ai/context.md` up to date: if you add, move, or remove major
directories/components, or change core conventions, update that file in the
same change.

## Scope of Analysis

When answering questions or exploring the repository, **ignore files that are
not tracked in version control** (e.g. untracked/gitignored files, build
artifacts, `__pycache__`, `.ipynb_checkpoints`, local outputs, `.venv`, etc.)
unless the user explicitly asks about them. Use `git ls-files` / `git status`
to distinguish tracked from untracked content when in doubt.

## Unix Philosophy

Favor small, composable pieces over monolithic ones:

- Each container/script/workflow step should **do one thing well** (subset data,
  convert a format, extract metadata, run a model) rather than bundling multiple
  responsibilities.
- Prefer plain text / JSON / JSON-LD for data interchange between steps so
  output from one tool can be piped into or consumed by another.
- Steps should be composable: an Argo workflow chains single-purpose containers
  together rather than one container doing everything end-to-end.
- Avoid unnecessary interactivity — CLI entry points should accept arguments/flags
  (see `typer` usage below) and run non-interactively so they can be automated.
- Keep it simple: don't add abstraction, configuration, or generality that
  isn't needed yet.

## Coding Conventions

**Python**
- Use `#!/usr/bin/env python3` shebang on executable entry-point scripts
  (e.g. `entry.py`).
- Use [`typer`](https://typer.tiangolo.com/) for CLI argument parsing on
  container entry points; use `pathlib.Path` for file/directory arguments with
  descriptive `help=` text.
- Prefer `pydantic` (and `pydantic_yaml`) models for structured config/metadata
  rather than untyped dicts, matching `schema/src/*.py`.
- Group imports as: stdlib, then third-party, then local/project modules
  (see `containers/cfe/src/entry.py`).
- Use the standard `logging` module (not `print`) for status/diagnostic output
  in long-running or containerized scripts.
- Follow existing naming: `snake_case` for functions/variables, module-level
  scripts named `entry.py` as the container's executable entry point.

**Shell scripts**
- Use `#!/bin/bash` shebang.
- Keep build/run scripts small and single-purpose (`build.sh`, `run.sh`,
  `test.sh`, `debug.sh`) — one script per action, not one script with modes.
- Docker image tags follow `cuahsi/<component>:<tag>` (e.g. `cuahsi/tif2cog:latest`).

**Docker**
- One `Dockerfile` per container under `containers/<name>/`, paired with a
  `build.sh` (or `build-docker-image.sh`) that builds it and an `entry.py`
  (or `entry.sh`) as the `ENTRYPOINT`.

**Argo Workflows (YAML)**
- One workflow family per directory under `workflows/`; keep workflow YAML
  focused on orchestration (chaining containers), not business logic.
- Parameterize workflows (`-p key=value`) instead of hardcoding values, so the
  same workflow can be reused across inputs/environments.

**Metadata schema (`schema/`)**
- Express metadata using Schema.org vocabulary and JSON-LD (`"@type"`, etc.);
  extend `schema/src/{base,core,dataset,datavariable}.py` for new
  domain-specific properties rather than editing the generated
  `schema_models/` library.
- Update the corresponding narrative doc in `schema/doc/*.md` whenever a
  metadata property is added or changed.
