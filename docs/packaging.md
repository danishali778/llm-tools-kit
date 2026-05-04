# Packaging

This project uses Hatchling as its build backend.

## Local install

For development:

```bash
python -m pip install -e ".[dev]"
```

For a runtime-only editable install:

```bash
python -m pip install -e .
```

## Build artifacts

To build a source distribution and wheel locally:

```bash
python -m build
```

Artifacts are written to:

```txt
dist/
```

The repository ignores build outputs by default.

## Metadata

Package metadata is defined in `pyproject.toml`, including:

- package name and version
- Python version requirement
- dependencies
- authors
- license
- classifiers
- project URLs

If you change the public package identity, update both `pyproject.toml` and the README.

## CI packaging checks

GitHub Actions validates package builds separately from the normal lint/test workflow.

Current build verification checks that:

- the project installs
- sdist and wheel artifacts can be built
- artifacts are available for inspection in workflow runs

## Release skeleton

The repository includes a release-oriented workflow that builds artifacts on tags or manual runs.

It does not publish to PyPI yet.

That later step should be added only after:

- package metadata is stable
- versioning discipline is agreed
- PyPI trusted publishing or credentials are configured

## Recommended release sequence

Until PyPI publishing is enabled, the safe process is:

1. merge the release-ready work to `main`
2. update version metadata in `pyproject.toml`
3. tag the release
4. let GitHub Actions build the release artifacts
5. inspect artifacts before enabling public publishing in a later phase
