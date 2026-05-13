# Current State

## What This Repo Is

`ha-dreame` is the new development track for a standalone Dreame product.

It exists in parallel with the currently working Dreame solution in `ha-config`.

## What Still Lives In `ha-config`

- the production `pyscript` queue runtime
- the production Dreame dashboard card
- the production dashboards and automations that consume the old entities and services
- production bug fixes for the running setup

## What Starts Here

- the future `ha_dreame` custom integration
- the future standalone Dreame card package
- migration-safe design work that must not break the current installation

## Guardrails

- Do not reuse the old `dreame_queue` service names in the new implementation.
- Do not claim parity with the production setup until both behavior and operator workflow are proven.
- Treat this repo as additive until an explicit cutover plan exists.
- Default new runtime behavior to read-only / command-disabled while both implementations are installed.
- Require explicit operator enablement before `ha_dreame` sends robot commands.
