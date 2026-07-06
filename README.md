# ha-dreame

`ha-dreame` is a standalone Home Assistant custom integration and dashboard card for testing a Dreame room-cleaning queue beside an existing `dreame_vacuum` setup.

This repository is still an alpha product track, but the migration cutover has happened in the maintainer's HAOS setup. The integration is now the product source for Dreame queue behavior and is intended to become a public HACS custom repository.

## Current Status

- Home Assistant domain: `ha_dreame`
- Upstream dependency: an already configured `dreame_vacuum` vacuum entity
- Default mode: command-disabled and safe for read-only initial installation
- Dashboard card: packaged with the integration and served from a namespaced static URL
- Cutover status: primary in the maintainer's HAOS setup; private HA wiring lives outside this public repo

## Installation

Use HACS custom repository installation for public alpha testing.

1. In HACS, add this repository as a custom repository with category `Integration`.
2. Install `HA Dreame`.
3. Restart Home Assistant.
4. Add the `HA Dreame` integration from Home Assistant's integrations UI.
5. Select the existing Dreame vacuum entity provided by `dreame_vacuum`.
6. Leave `allow_robot_commands` disabled for initial validation.

Alpha builds may be published as GitHub prerelease versions. If HACS does not
offer the expected alpha tag as the latest version, open the repository in HACS,
enable beta or prerelease visibility, and explicitly select the alpha tag before
restarting Home Assistant.

For local development, see [docs/parallel-install.md](docs/parallel-install.md). Keep machine-specific paths, hostnames, users, tokens, and entity ids out of committed files.

For alpha candidate validation in Home Assistant, follow
[docs/alpha-test-plan.md](docs/alpha-test-plan.md).

For release parity tracking against the previous controller, follow
[docs/parity-checklist.md](docs/parity-checklist.md).

## Configuration

The config flow selects an existing Dreame vacuum. The integration validates that the selected entity exists and is a vacuum before setup completes.

Important options:

- `allow_robot_commands`: disabled by default. When disabled, active robot command services fail before dispatching commands.
- `auto_reconcile_enabled`: disabled by default. Automatic reconcile only runs when both this option and `allow_robot_commands` are enabled.
- Companion observation entities: optional explicit sensor ids for installations where the derived `sensor.<robot>_state`, `sensor.<robot>_task_status`, or `sensor.<robot>_error` names do not match.

Before a controlled command window, call `ha_dreame.get_control_readiness` for
the config entry. It reports the command gate, selected vacuum availability,
queue state, companion entities for running overrides, and the actions that are
currently safe to test without sending any robot command.

## Dashboard Card

The integration serves the packaged queue card from:

```yaml
url: /ha_dreame/frontend/ha-dreame-queue-card.js
type: module
```

Example card configuration:

```yaml
type: custom:ha-dreame-queue-card
entity: sensor.ha_dreame_queue_status
```

The card includes a Lovelace editor for the queue entity and title. When Home Assistant exposes a `ha_dreame` queue status sensor, the editor can suggest that sensor; otherwise use the generic entity shape above and adjust it to the entity created by your config entry.

During an active queue run, the card shows a dedicated interrupted state when the selected robot
reports paused/error signals. In that state it offers command-gated Continue and End controls,
matching the operator workflow exposed by Dreame while keeping `allow_robot_commands` authoritative.

## Safety Model

- `ha_dreame` owns its own services, entities, storage keys, and card identifiers under the `ha_dreame` namespace.
- The integration depends on `dreame_vacuum`; it does not replace or authenticate to the robot directly.
- Active robot commands require explicit operator enablement through `allow_robot_commands`.
- Parallel installation of multiple controllers for the same robot is not a target. Avoid parallel active control.

## Current Limitations

- This is an alpha migration project, not a stable release.
- Real-world parity with the previous private queue and dashboard has passed initial cutover use, but remaining release hardening is still tracked in issues.
- Automatic reconciliation is opt-in and should remain disabled unless a user deliberately wants command-gated automatic reconcile.
- Brand assets for HACS presentation are tracked separately from runtime readiness.
- The public repository intentionally avoids private room names, dashboard files, local hostnames, and local entity ids.

## Removal

Rollback should leave the existing `dreame_vacuum` integration untouched.

1. Disable `allow_robot_commands`.
2. Disable `auto_reconcile_enabled`.
3. Remove or unload the `HA Dreame` config entry.
4. Remove the dashboard card resource if it was added manually.
5. Uninstall the HACS custom repository or remove the local custom component files.
6. Restart Home Assistant when removing custom integration files.

## Validation

Local development is Dockerized. The only required local runtime tool is Docker;
Python 3.13, Node 22, npm, and Python test dependencies are provided by the dev
image.

```bash
./scripts/dev check
```

Focused checks:

```bash
./scripts/dev python-check
./scripts/dev frontend-check
./scripts/dev test-python
./scripts/dev test-frontend
./scripts/dev shell
```

The dev image uses Python 3.13 and Node 22 to match the supported Home Assistant
and frontend validation targets. GitHub Actions also uses `./scripts/dev` for
Python and frontend validation, and separately runs HACS validation and Hassfest.

## Development Notes

- Use TDD for functional changes and bug fixes.
- Keep commits conventional and preserve red/green chains.
- Update [docs/dreame-behavior-knowledge.md](docs/dreame-behavior-knowledge.md) when runtime debugging reveals durable Dreame behavior.
- Keep public docs and examples generic.
