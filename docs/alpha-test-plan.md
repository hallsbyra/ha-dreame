# Alpha Test Plan

## Goal

Validate an alpha candidate of `ha_dreame` in Home Assistant as the primary
Dreame queue controller.

The alpha test is successful when the integration installs, configures, exposes
the expected read-only state, loads the packaged dashboard card, and can run one
controlled command-gated smoke test without namespace or command-gate problems.

## Preconditions

- A current `ha-dreame` branch or release candidate has green Validate, HACS,
  and Hassfest checks.
- The existing `dreame_vacuum` integration is already configured in Home
  Assistant and exposes one vacuum entity.
- The tester has a rollback path and can restart Home Assistant.
- Leave `allow_robot_commands` disabled for initial validation.
- Leave `auto_reconcile_enabled` disabled for initial validation.

Keep command windows narrow and deliberate until the candidate has passed the
read-only and dashboard smoke checks.

## Preflight Validation

Run the repository gates before installing the candidate:

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

If any local Python dependencies are unavailable, use the GitHub Actions
Validate, HACS, and Hassfest results as the release candidate preflight gate.

Before promoting an alpha toward beta, update
`docs/parity-checklist.md` with the candidate's runtime evidence and remaining
gates.

## HACS Prerelease Versions

Alpha tags may be published as a GitHub prerelease. HACS can install these
versions, but they may not appear as the normal latest version in the update
entity.

When validating a GitHub prerelease through HACS:

1. Open the repository in HACS.
2. Enable beta or prerelease visibility for the repository if the alpha tag is
   not listed.
3. If needed, explicitly select the alpha tag to download or install.
4. Restart Home Assistant after an integration update.
5. Confirm the HACS update entity shows the expected installed version.

If HACS still reports an older latest version after the prerelease install, use
the installed version as the source of truth for the candidate under test and
record that behavior in the release evidence.

## Install Candidate

Prefer HACS for alpha validation because it exercises the public custom
repository install path.

1. Add the repository to HACS as a custom repository with category
   `Integration`.
2. Install `HA Dreame`.
3. For alpha prereleases, enable beta or prerelease visibility and explicitly
   select the alpha tag if HACS does not offer it as the latest version.
4. Restart Home Assistant.
5. Add the `HA Dreame` integration from the integrations UI.
6. Select the existing Dreame vacuum entity provided by `dreame_vacuum`.
7. Keep `allow_robot_commands` disabled.
8. Keep `auto_reconcile_enabled` disabled.

Local development copies are acceptable for focused debugging, but do not commit
machine-specific paths, hostnames, tokens, entity ids, or room names.

## Read-Only Smoke Test

With robot commands disabled:

1. Confirm the config entry loads without setup errors.
2. Confirm a `ha_dreame` queue status sensor exists.
3. Call `ha_dreame.get_control_readiness` for the config entry and confirm
   `ready_for_read_only_observation` is true while
   `ready_for_control_window` is false.
4. Call `ha_dreame.get_runtime_status` for the config entry and inspect the
   queue snapshot.
5. Call `ha_dreame.evaluate_reconcile` and confirm it reports observations
   without mutating queue state or sending robot commands.
6. Download diagnostics and confirm they contain no secrets or private runtime
   values.
7. Confirm no unexpected setup, service, or namespace errors appear in Home
   Assistant logs.

## Dashboard Card Smoke Test

Load the packaged card through the namespaced resource URL:

```yaml
url: /ha_dreame/frontend/ha-dreame-queue-card.js
type: module
```

Add a generic card:

```yaml
type: custom:ha-dreame-queue-card
entity: sensor.ha_dreame_queue_status
```

Validate:

- the card renders without console errors
- the Lovelace editor opens
- the queue entity can be selected or entered manually
- available rooms render when Home Assistant exposes them from the vacuum entity
- add/remove/move/update controls mutate only the `ha_dreame` queue state
- active controls are visible only when the card state allows them

## Controlled Command Smoke Test

Only run this test in a short controlled window.

Do not let two integration instances or controllers send robot commands to the same robot.

1. Confirm no other integration instance or controller is about to start or continue a run.
2. Add one low-risk room to the `ha_dreame` queue.
3. Call `ha_dreame.get_control_readiness` and confirm the queue has a pending
   item, the selected vacuum is available, and only `allow_robot_commands` is
   blocking control readiness.
4. Enable `allow_robot_commands`.
5. Call `ha_dreame.get_control_readiness` again and confirm `start_queue` is in
   `available_actions`.
6. Keep `auto_reconcile_enabled` disabled unless this exact test targets
   automatic reconciliation.
7. Start the queue from `ha_dreame`.
8. Observe the queue status sensor, robot state, task status, and Home Assistant
   logs.
9. Test either skip or cancel, not both, unless the first command path is clean.
10. Disable `allow_robot_commands` after the command window.

If the robot reports a durable new state transition, update
`docs/dreame-behavior-knowledge.md` and add or plan test coverage.

## Rollback

Rollback should leave the existing `dreame_vacuum` integration untouched.

1. Disable `allow_robot_commands`.
2. Disable `auto_reconcile_enabled`.
3. Unload or remove the `HA Dreame` config entry.
4. Remove the dashboard resource if it was added manually.
5. Uninstall the HACS custom repository or remove the local custom component
   files.
6. Restart Home Assistant if custom integration files were removed.

## Evidence To Capture

Capture public-safe evidence for the release issue or follow-up PR:

- commit SHA or release tag under test
- GitHub Actions run links for Validate, HACS, and Hassfest
- Home Assistant version
- HACS installed version and whether beta or prerelease visibility was needed
- whether install, config flow, queue sensor, services, diagnostics, and card
  loading passed
- whether command testing was skipped or completed
- anonymized state transitions that should update
  `docs/dreame-behavior-knowledge.md`
- any blocker that prevents alpha release
