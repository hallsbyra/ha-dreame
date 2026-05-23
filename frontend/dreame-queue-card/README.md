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
- Keep service/entity assumptions under the `ha_dreame` namespace.
- Use public-safe examples such as `vacuum.robot` and generic room names.
- Keep legacy card behavior as a reference, not as copied private dashboard config.

## Validation

```bash
npm ci
npm run check
```

The build output is `dist/ha-dreame-queue-card.js`. It is a development artifact for the future card packaging flow and is not a cutover signal by itself.
