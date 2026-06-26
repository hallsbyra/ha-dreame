# ha-dreame

`ha-dreame` is a standalone Home Assistant custom integration and dashboard card for testing a Dreame room-cleaning queue beside an existing `dreame_vacuum` setup.

This repository is still an alpha migration track. The integration is intended to become a public HACS custom repository, but it is not a drop-in replacement for an existing private Dreame controller yet.

## Current Status

- Home Assistant domain: `ha_dreame`
- Upstream dependency: an already configured `dreame_vacuum` vacuum entity
- Default mode: command-disabled and safe for read-only parallel installation
- Dashboard card: packaged with the integration and served from a namespaced static URL
- Cutover status: no production cutover is implied by installing this repository

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

## Safety Model

- `ha_dreame` uses separate services, entities, storage keys, and card identifiers from legacy `pyscript.dreame_queue_*` paths.
- The integration depends on `dreame_vacuum`; it does not replace or authenticate to the robot directly.
- Active robot commands require explicit operator enablement through `allow_robot_commands`.
- Parallel installation is supported for migration testing. Parallel active control of the same robot by two controllers is not a target.
- Keep the old controller as the production path until a separate cutover issue and PR exist.

## Current Limitations

- This is an alpha migration project, not a stable release.
- Real-world parity with the previous private queue and dashboard still needs controlled runtime validation.
- Automatic reconciliation is opt-in and should remain disabled during initial parallel testing.
- Brand assets for HACS presentation are tracked separately from runtime readiness.
- The public repository intentionally avoids private room names, dashboard files, local hostnames, and local entity ids.

## Removal

Rollback should leave the existing `dreame_vacuum` integration and any legacy controller untouched.

1. Disable `allow_robot_commands`.
2. Disable `auto_reconcile_enabled`.
3. Remove or unload the `HA Dreame` config entry.
4. Remove the dashboard card resource if it was added manually.
5. Uninstall the HACS custom repository or remove the local custom component files.
6. Restart Home Assistant when removing custom integration files.

## Validation

```bash
python -m ruff check .
python -m ruff format --check .
python -m pyright
python -m compileall custom_components/ha_dreame
python -m pytest
cd frontend/dreame-queue-card
npm ci
npm run check
```

GitHub Actions also runs Python validation, frontend validation, HACS validation, and Hassfest.

## Development Notes

- Use TDD for functional changes and bug fixes.
- Keep commits conventional and preserve red/green chains.
- Update [docs/dreame-behavior-knowledge.md](docs/dreame-behavior-knowledge.md) when runtime debugging reveals durable Dreame behavior.
- Keep public docs and examples generic.
