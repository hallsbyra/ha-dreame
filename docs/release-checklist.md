# Release Checklist

## Alpha

- [ ] HACS validation passes.
- [ ] Hassfest passes.
- [ ] Python tests pass with the configured coverage gate.
- [ ] Python type validation passes with `python -m pyright`.
- [ ] Config flow works in a clean Home Assistant test environment.
- [x] README documents installation, removal, and current limitations.
- [x] Alpha candidate validation is documented in `docs/alpha-test-plan.md`.
- [ ] No secrets, private entity ids, private paths, or local hostnames are present.
- [ ] Release notes clearly mark the release as experimental.
- [ ] HACS prerelease visibility or explicit version selection is documented for alpha tags.

## Beta

- [ ] Queue core has tests for creation, mutation, start, cancel, skip, completion, and drift.
- [ ] Behavior knowledge regressions have corresponding automated tests.
- [ ] Read-only/default command-disabled behavior is verified while installed beside the old implementation.
- [ ] Robot command dispatch is explicitly opt-in.
- [ ] The integration can coexist with the old production implementation.
- [ ] Known limitations and troubleshooting are documented.

## Release Candidate

- [ ] `docs/parity-checklist.md` is complete against the current production queue.
- [ ] Frontend card or documented dashboard path works against `ha_dreame` entities/services.
- [ ] Diagnostics and failure reporting are sufficient for runtime debugging.
- [ ] HACS brand/readiness work is complete or explicitly tracked.
- [ ] Cutover issue exists before any private production cleanup starts.

## Stable

- [ ] A tagged GitHub release exists with clear release notes.
- [ ] HACS installation from the release has been verified.
- [ ] Migration and rollback instructions are documented.
- [ ] Public docs do not reveal private runtime details.
