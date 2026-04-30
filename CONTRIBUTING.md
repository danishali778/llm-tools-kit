# Contributing

This repository is built incrementally through small, reviewable pull requests.

The current development style is opinionated on purpose:

- branch from `main`
- keep commits atomic
- keep PRs focused
- run Ruff and Pytest before pushing
- merge with `rebase` by default so commits stay visible on `main`

## Development Setup

Requirements:

- Python `3.11+`
- Git

Install the project in editable mode with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

If you use a virtual environment locally:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Local Checks

Before pushing a branch, run:

```bash
python -m ruff check .
python -m pytest
```

The GitHub Actions workflow runs the same checks on:

- Python `3.11`
- Python `3.12`

## Branch Workflow

Always start new work from the latest `main` unless the work is explicitly part of the same in-flight PR.

```bash
git switch main
git pull origin main
git switch -c <branch-name>
```

Examples:

- `phase-4-safety-context`
- `fix/file-tool-limit`
- `docs/readme-refresh`

Avoid stacked PRs unless the new branch truly depends on an unmerged branch. Independent work should not branch from another feature branch.

## Commit Style

Use small atomic commits. Each commit should represent one logical change.

Good examples:

- `feat: add JSON utility tools`
- `feat: add text chunking tool`
- `fix: configure hatch package discovery`
- `test: make file path assertions portable`
- `docs: rewrite repository README`

Avoid mixing multiple concerns in one commit when they can be split cleanly.

## Pull Requests

Open one PR per focused unit of work.

Good PR shape:

- one feature area
- one bug fix area
- one documentation slice

PRs should include:

- a short summary of what changed
- validation commands you ran
- notable limitations or follow-up work

Contributors should submit changes through pull requests rather than pushing directly to `main`.

Repository maintainers decide:

- whether a PR is ready
- whether it should be merged
- when it should be merged
- which merge method should be used

Draft PRs are fine during development. Mark them ready when the scope is complete and checks are passing.

## Merge Strategy

Default merge method:

```txt
Rebase merge
```

Why:

- preserves atomic commits on `main`
- keeps history linear
- keeps PR commit structure visible after merge

This merge strategy is a maintainer decision at merge time. Opening a PR does not imply it will be merged automatically.

Do not use squash merge by default for this repository.

Use merge commits only if there is a specific reason to preserve the branch boundary in history.

## Repository Structure

Current layout:

```txt
src/
  agent_tools/
    core/
    adapters/
    tools/
    safety/

tests/
examples/
```

Conventions:

- `core/` contains the registry, execution model, result objects, and errors
- `adapters/` contains provider-specific schema/export helpers
- `tools/` contains reusable built-in tools
- `safety/` contains focused safety helpers
- `tests/` mirrors the area being changed
- `examples/` shows small runnable usage patterns

## Adding New Tools

When adding a built-in tool:

1. Put the implementation in the correct module under `src/agent_tools/tools/` or `src/agent_tools/safety/`
2. Decorate public tool functions with `@tool`
3. Export them through the relevant `__init__.py`
4. Add focused tests
5. Add or update an example if the tool is user-facing
6. Update documentation if the public surface changed

Keep tool behavior predictable. Prefer narrow, dependable utilities over clever but unstable ones.

## Testing Guidance

Tests should:

- cover direct function use when relevant
- cover registry execution paths
- cover normal and failure cases
- stay platform-neutral where possible
- avoid real network access
- avoid requiring API keys for normal CI

If a provider example needs credentials, gate it behind an environment variable and keep it out of normal test runs.

## Environment Variables

Real secrets must never be committed.

Use:

- `.env.example` for documented placeholders
- local `.env` files for real credentials

The repository already ignores:

- `.env`
- `.env.*`

while keeping:

- `.env.example`

## Documentation

Documentation changes should track the real implementation on `main`.

Do not describe features as available if they are still only planned.

When updating the README or contributor docs:

- prefer concrete examples over vague marketing text
- describe current limitations honestly
- keep instructions aligned with the actual CI and package layout

## Questions and Scope

If a change grows beyond one coherent PR, split it.

The repository is intentionally being built phase by phase. Respect the current scope instead of jumping ahead into unrelated integrations.
