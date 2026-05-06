# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-05-06

### Added
- MkDocs Material documentation site auto-deployed to GitHub Pages
  on every push to `main`, with an API reference page generated from
  source docstrings via `mkdocstrings`.
- `ioc-classify` command-line entry point. Reads one IOC per line from
  a file or stdin and emits TSV (default) or JSON Lines, with graceful
  handling of `BrokenPipeError` for pipeline use.
- Pre-commit hygiene hooks (trailing whitespace, EOF newline, YAML/TOML
  validity, merge-conflict markers, large files, case conflicts).
- `pip-audit` dependency-vulnerability job in CI.
- Hypothesis property-based tests covering the classifier contract for
  any IPv4/IPv6 address and any 32/40/64 hex string.
- Codecov integration with coverage badge in README.
- `examples/` directory with a runnable file-classification script.
- Dependabot configuration for `pip` and `github-actions` with a 7-day
  cooldown and grouped, labelled PRs.
- Trusted Publishing release workflow that publishes to PyPI on `v*`
  tag push via OIDC (no API token).
- Status and metadata badges in README (CI, Codecov, PyPI version,
  Python versions, license, Ruff).

### Changed
- Pinned every dev dependency to a specific version for reproducible
  installs across CI runs and contributor environments.

## [0.2.0] - 2026-04-27

### Added
- `py.typed` marker; full inline type annotations exposed to downstream
  type checkers.
- `mypy --strict` enforcement across `src/` and `tests/` (with a
  relaxed override on tests).
- `ClassificationResult` `TypedDict` describing every value returned
  by `IOCClassifier.classify`.
- FQDN trailing-dot form accepted for both domain and URL host
  (RFC 1034).
- Schemeless URL form support (host followed by any combination of
  port, path, query, or fragment).
- Python 3.13 added to the supported and tested matrix.

### Changed
- Migrated build backend from setuptools to Hatchling; package version
  is single-sourced from `src/ioc_typing/__init__.py`.
- Migrated env/script orchestration from tox + Makefile to Hatch envs.
- Replaced black, isort, and flake8 with Ruff.
- Bumped minimum supported Python to 3.10.

## [0.1.0] - 2024-12-15

### Added
- Initial release of `IOCClassifier` with regex-based detection of
  IPv4, IPv6, MD5/SHA1/SHA256, URL, and domain types.
