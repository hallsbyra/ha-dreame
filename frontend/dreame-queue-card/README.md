# dreame-queue-card

Frontend package for the future standalone HA Dreame dashboard card.

The package starts with pure helpers and tests before runtime UI wiring. The production card still lives outside this repo until cutover.

## Current Scope

- Parse the public `ha_dreame` queue status sensor attribute shape.
- Keep service/entity assumptions under the `ha_dreame` namespace.
- Use public-safe examples such as `vacuum.robot` and generic room names.
- Keep legacy card behavior as a reference, not as copied private dashboard config.

## Validation

```bash
npm ci
npm run check
```
