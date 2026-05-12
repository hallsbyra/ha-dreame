# Merge Policy

## Default

Use rebase merge for normal feature PRs.

This keeps `main` linear while preserving the red/green/refactor commit chain that matters for
TDD review. Do not squash TDD feature branches unless the PR explicitly states that preserving the
intermediate commits is not useful.

## Commit Shape

Prefer focused commits with Conventional Commit subjects:

- `test:` for failing or regression coverage
- `feat:` for new behavior
- `fix:` for bug fixes
- `refactor:` for structure changes after tests are green
- `docs:`, `ci:`, and `chore:` for non-runtime changes

## Exceptions

Squash merge can be used for documentation-only, metadata-only, or generated-output PRs when there
is no meaningful red/green history to preserve.

Merge commits should be avoided unless a branch carries long-running coordination history that would
be harder to understand as a linear series.
