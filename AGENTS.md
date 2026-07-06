# AGENTS.md

## Scope
This repository is the standalone Dreame product track.

## Current Status
- `ha-dreame` is the primary Dreame queue product after cutover.
- `ha-config` owns private HA dashboard wiring, automations, deploy and runtime checks for the installed HACS integration.
- The old private Dreame queue path has been removed from `ha-config`; do not reintroduce product logic there.

## Product Direction
- Target product: a standalone Home Assistant integration under the domain `ha_dreame`.
- Long-term goal: HACS-friendly packaging and release flow.
- Migration model: public HACS product with private HA wiring kept outside this repo.
- Namespace rule: keep new services, events, entity ids and card identifiers under `ha_dreame`.
- Command safety rule: new runtime behavior starts read-only / command-disabled by default. Any code path that sends robot commands must require explicit operator enablement before it can run.
- Public repo rule: do not commit secrets, local hostnames, private paths, local-only entity ids, or assumptions from one Home Assistant installation.
- Dependency rule: it is acceptable for this integration to depend explicitly on the existing `dreame_vacuum` integration, but runtime setup must still validate that the selected dependency exists and is usable.

## Repository Map
- `custom_components/ha_dreame/` - Home Assistant integration
- `frontend/dreame-queue-card/` - standalone Dreame dashboard card
- `docs/` - migration guardrails and product notes
- `docs/dreame-behavior-knowledge.md` - public-safe observed Dreame behavior and regression knowledge
- `docs/merge-policy.md` - merge strategy for preserving TDD commit chains
- `docs/parallel-install.md` - public-safe local and HAOS parallel-install workflow
- `docs/alpha-test-plan.md` - public-safe Home Assistant alpha candidate validation plan
- `docs/release-checklist.md` - release readiness gates

## Validation
- Local development validation is Dockerized. Do not require host Python,
  Node, npm, venv, or frontend tooling.
- Required local tool:
  - `docker`
- Full local check:
  - `./scripts/dev check`
- Python validation:
  - `./scripts/dev python-check`
- Frontend card package:
  - `./scripts/dev frontend-check`
- Interactive development shell:
  - `./scripts/dev shell`
- GitHub Actions uses the same Docker runner for Python and frontend validation,
  and also runs HACS validation and Hassfest.

## Development Model
- Use TDD for all functional changes and bug fixes.
- Prefer visible red/green/refactor commit chains:
  - `test:` commits add failing coverage for the expected behavior.
  - `feat:` or `fix:` commits make those tests pass.
  - `refactor:` commits are allowed after tests are green.
- Prefer rebase merge for normal PRs so `main` stays linear while the red/green chain is preserved.
- Do not squash TDD branches unless the PR explicitly says the intermediate commits are not useful.
- Keep feature branches small and centered on one behavior slice.
- Use Conventional Commits for commits made in this repo.
- Treat historical private implementation details as migration reference material only, not as a runtime dependency.
- Keep implementation code deterministic and testable before wiring it to Home Assistant runtime APIs.
- Track quality-scale progress in `custom_components/ha_dreame/quality_scale.yaml`.

## Deploy
- Release through HACS/GitHub releases, then update the installed integration in HAOS.
- Private HA dashboard/automation deploy belongs in `../ha-config`.
- Local development deploys may install `ha_dreame` into a Home Assistant test environment. Robot command dispatch must stay disabled unless explicitly enabled by the operator.
- For local or HAOS install work, follow `docs/parallel-install.md` and keep examples public-safe.

## Working Rules
- If the task is Dreame product logic, frontend card behavior, tests, release, or behavior knowledge, work here.
- If the task is private HA dashboard wiring, automations, deploy, runtime checks, or local Home Assistant configuration, work in `../ha-config`.
- Keep private HA details out of this public repo.

## Dreame Behavior Knowledge
- Update `docs/dreame-behavior-knowledge.md` whenever runtime debugging reveals durable Dreame behavior that should influence queue logic.
- Keep behavior entries public-safe:
  - use generic entity examples such as `vacuum.<robot>` and `sensor.<robot>_task_status`
  - avoid private room names, local hostnames, user names, secrets, tokens, and private paths
  - anonymize timestamps or examples when exact details are not needed for the behavior
- Turn confirmed regressions or state-machine rules into automated tests in the same or next focused slice.
- Mark each behavior as `Observed`, `Inferred`, or `Unknown` so future changes do not overfit weak evidence.
