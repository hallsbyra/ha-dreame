# AGENTS.md

## Scope
This repository is the greenfield Dreame product track.

The current production Dreame implementation still lives in the sibling repo `../ha-config`.

## Current Status
- `ha-config` is still the production path for Dreame queue behavior, dashboards and bug fixes.
- `ha-dreame` is the future standalone replacement track.
- Do not remove or rename production Dreame pieces in `ha-config` from work done here unless the user explicitly asks for cutover work.

## Product Direction
- Target product: a standalone Home Assistant integration under the domain `ha_dreame`.
- Long-term goal: HACS-friendly packaging and release flow.
- Migration model: run in parallel with the old implementation until feature parity is reached.
- Collision rule: keep new services, events, entity ids and card identifiers isolated from the current `pyscript.dreame_queue_*` implementation.

## Repository Map
- `custom_components/ha_dreame/` - future Home Assistant integration
- `frontend/dreame-queue-card/` - future home for the standalone Dreame dashboard card
- `docs/` - migration guardrails and product notes

## Validation
- Python scaffold check:
  - `python -m compileall custom_components/ha_dreame`

## Deploy
- This repo is not the production deploy path yet.
- Do not deploy this scaffold to HAOS as a replacement for the running Dreame solution without explicit user approval.

## Working Rules
- If the task is to fix the currently running Dreame setup, work in `../ha-config`.
- If the task is to build the next-generation Dreame component, work here.
- Prefer additive migration work over in-place replacement work.
