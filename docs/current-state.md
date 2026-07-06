# Current State

## What This Repo Is

`ha-dreame` is the standalone Dreame product track.

It is the primary Dreame queue implementation after cutover in the maintainer's HAOS setup.

## What Still Lives In `ha-config`

- private dashboard wiring for the installed HACS card
- private automations that consume `ha_dreame` entities
- deploy and runtime validation against HAOS
- other unrelated local Home Assistant `pyscript` code

## What Lives Here

- the `ha_dreame` custom integration
- the standalone packaged Dreame card
- product behavior, tests, release docs and public-safe behavior knowledge

## Guardrails

- Keep services, entities, events, storage keys and frontend identifiers under `ha_dreame`.
- Keep private HA dashboards, room names, hostnames and local entity ids out of this repo.
- Default new runtime behavior to read-only / command-disabled on fresh installs.
- Require explicit operator enablement before `ha_dreame` sends robot commands.
