# dreame-queue-card

Frontend package for the future standalone HA Dreame dashboard card.

The package starts with pure helpers and tests before runtime UI wiring. The production card still lives outside this repo until cutover.

## Current Scope

- Parse the public `ha_dreame` queue status sensor attribute shape.
- Resolve and cycle queue item cleaning overrides for future controls.
- Map running override display values while keeping active changes behind a future `ha_dreame` service gate.
- Derive queue activity labels from public robot, task-status, and error signals.
- Build a first read-only `ha-dreame-queue-card` custom element.
- Extract Dreame room maps and show available rooms read-only.
- Add available rooms through the `ha_dreame.add_queue_room` queue service without dispatching robot commands.
- Remove pending queue items through the `ha_dreame.remove_queue_item` queue service.
- Move pending queue items and clear pending items through namespaced `ha_dreame` queue services.
- Cycle pending queue item overrides through the `ha_dreame.update_queue_item_overrides` queue service.
- Start, cancel, and skip queues through existing command-gated `ha_dreame` services.
- Provide a Lovelace card editor and public-safe stub config for Home Assistant dashboard setup.
- Keep service/entity assumptions under the `ha_dreame` namespace.
- Use public-safe examples such as `vacuum.robot` and generic room names.
- Keep legacy card behavior as a reference, not as copied private dashboard config.

## Validation

```bash
npm ci
npm run check
```

The build output is packaged into `custom_components/ha_dreame/frontend/ha-dreame-queue-card.js`.
When the integration is loaded, Home Assistant serves it from `/ha_dreame/frontend/ha-dreame-queue-card.js`.

Add the packaged module as a dashboard resource:

```yaml
url: /ha_dreame/frontend/ha-dreame-queue-card.js
type: module
```

The card exposes a Lovelace editor. When Home Assistant can see a public `ha_dreame`
queue status sensor, the default card config uses that entity. If no queue sensor is
detectable yet, the fallback remains generic and public-safe:

```yaml
type: custom:ha-dreame-queue-card
entity: sensor.ha_dreame_queue_status
```

Keep dashboard examples generic. Do not commit private dashboard files, local entity ids, room names, or host-specific resource paths.
