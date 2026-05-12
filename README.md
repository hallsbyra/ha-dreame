# ha-dreame

Greenfield Dreame product repo for the next-generation Home Assistant integration and dashboard card.

## Status

This repository is intentionally a scaffold.

- Production Dreame behavior still runs from `ha-config`.
- This repo is the parallel replacement track.
- Nothing here should be treated as a drop-in replacement yet.

## Current Goal

Build a standalone Dreame solution that can eventually replace the current mix of `pyscript` logic and custom card code living in `ha-config`.

## Principles

- Keep the existing production path stable while the new path is developed.
- Use new namespaces so both systems can coexist during migration.
- Move toward a HACS-friendly custom integration under `custom_components/ha_dreame/`.
- Move the future Dreame card source into this repo instead of keeping it in the shared `ha-config/custom-cards` project.

## Layout

- `custom_components/ha_dreame/` - minimal integration scaffold
- `frontend/dreame-queue-card/` - future frontend package home
- `docs/current-state.md` - migration status and guardrails

## Validation

```bash
python -m ruff check .
python -m ruff format --check .
python -m compileall custom_components/ha_dreame
python -m pytest
```

GitHub Actions also runs HACS validation and Hassfest.

## GitHub

This repo is intended to become a public GitHub repository and future HACS custom repository.
