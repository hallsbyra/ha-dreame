# Parallel Install Guide

This guide describes how to install and test `ha_dreame` with an existing `dreame_vacuum` setup.

It is intentionally public-safe. Use placeholder paths and generic entity examples. Do not add private hostnames, private paths, exact local entity ids, tokens, secrets, or room names.

## Safety Model

- `ha_dreame` uses the Home Assistant domain `ha_dreame`, so its services and entities are namespaced.
- The integration depends on an existing `dreame_vacuum` vacuum entity. It does not replace that integration.
- `ha_dreame` is command-disabled by default. Active robot commands require the `allow_robot_commands` option to be enabled explicitly.
- Automatic reconcile is opt-in: auto reconcile is disabled by default and only runs when both `allow_robot_commands` and `auto_reconcile_enabled` are enabled.
- Do not let two controllers or integration instances send robot commands to the same robot at the same time. Parallel active command control is not a target.

## HACS Custom Repository Install

Use this path when testing a pushed branch, release, or public repository state through Home Assistant.

1. In HACS, add this repository as a custom repository with category `Integration`.
2. Install `HA Dreame`.
3. Restart Home Assistant.
4. Add the `HA Dreame` integration from the Home Assistant integrations UI.
5. Select the existing Dreame vacuum entity provided by `dreame_vacuum`.
6. Leave robot commands disabled during initial validation.

For Home Assistant OS, prefer the HACS path for repeatable installation. Do not document installation-specific SSH targets, hostnames, users, or add-on paths in this repository.

## Local Development Deploy

Use this path only for local development. Keep commands generic and substitute local paths outside committed files.

1. Validate the repo before copying files:

   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m compileall custom_components/ha_dreame
   python -m pytest
   ```

2. Copy or sync `custom_components/ha_dreame/` from this repository into the target Home Assistant config directory:

   ```bash
   rsync -a --delete custom_components/ha_dreame/ <ha-config>/custom_components/ha_dreame/
   ```

3. Restart Home Assistant.
4. Configure `HA Dreame` through the UI.
5. Do not commit machine-specific deploy scripts, hostnames, config paths, access tokens, or entity ids.

## First Setup

1. Confirm the existing `dreame_vacuum` integration is already configured and exposes one vacuum entity.
2. Add a `HA Dreame` config entry for that vacuum.
3. Keep `allow_robot_commands` disabled.
4. Keep `auto_reconcile_enabled` disabled.
5. If automatic observation needs non-conventional entity names, set explicit companion observation entities in options.
6. Restart or reload the config entry after changing options when Home Assistant asks for it.

## Dashboard Card Resource

The integration serves the packaged queue card from a namespaced static URL:

```yaml
url: /ha_dreame/frontend/ha-dreame-queue-card.js
type: module
```

Example card configuration:

```yaml
type: custom:ha-dreame-queue-card
entity: sensor.ha_dreame_queue_status
```

The card also exposes a Lovelace editor. After the resource is loaded, adding
`HA Dreame Queue` from the dashboard card picker should suggest a detected
`ha_dreame` queue status sensor when one exists. If the suggestion is not
available yet, set the queue entity manually with the generic shape above.

Keep dashboard examples generic. Do not commit private dashboard files, local entity ids, room names, or host-specific resource paths.

## Read-Only Validation

Start with read-only behavior on fresh installs.

Useful checks:

- the config entry loads without setup errors
- the queue status sensor exists under the `ha_dreame` namespace
- `ha_dreame.get_runtime_status` returns an inspectable queue snapshot
- `ha_dreame.evaluate_reconcile` returns observations and decisions without mutating runtime state
- diagnostics contain only public-safe config-entry information

Do not enable commands for read-only validation.

## Controlled Command Testing

Only use active commands in a short controlled window.

1. Ensure no other controller or integration instance is about to send robot commands for the same robot.
2. Enable `allow_robot_commands` in `HA Dreame` options.
3. Keep `auto_reconcile_enabled` disabled unless the test specifically covers automatic reconciliation.
4. Start with one simple room queue and observe the robot state before adding more pending work.
5. If testing automatic reconciliation, enable `auto_reconcile_enabled` only after confirming the command gate is intentionally enabled.
6. Watch Home Assistant logs and queue status after each command.
7. Disable `allow_robot_commands` again after the test window unless continuing controlled active testing.

## Rollback

Rollback should leave the existing `dreame_vacuum` integration untouched.

1. Disable `allow_robot_commands`.
2. Disable `auto_reconcile_enabled`.
3. Unload or remove the `HA Dreame` config entry.
4. Remove the local custom component files or uninstall the HACS custom repository if needed.
5. Restart Home Assistant when removing files or changing custom integration installation state.

## Runtime Observations

When testing reveals durable Dreame behavior, update `docs/dreame-behavior-knowledge.md` in the same PR or a follow-up slice.

Record observations generically:

- use examples like `vacuum.<robot>` and `sensor.<robot>_task_status`
- describe state transitions, not private home context
- include whether the behavior is `Observed`, `Inferred`, or `Unknown`
- turn confirmed regressions into automated tests
