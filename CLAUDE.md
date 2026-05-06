# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`ioc-typing` is a zero-dependency Python library that classifies a string as one of: IPv4/IPv6, domain, URL, or MD5/SHA1/SHA256 hash. The public API is `IOCClassifier` plus the `ClassificationResult` `TypedDict`, both exposed from `ioc_typing` (see `src/ioc_typing/__init__.py`). The package ships a `py.typed` marker so downstream type checkers consume the inline annotations.

## Common commands

All workflows go through `hatch` — both the build backend (hatchling) and env/script orchestration live in `pyproject.toml` under `[tool.hatch.*]`. Install hatch once with `pipx install hatch` (or `uv tool install hatch`).

- `hatch run test` — pytest in the default env. The `-v` and `--cov=ioc_typing` flags plus `testpaths = ["tests"]` come from `[tool.pytest.ini_options]` in `pyproject.toml`, not from the script definition (which is just `pytest {args}`).
- `hatch run lint` — `ruff format --check` and `ruff check` over `src tests`
- `hatch run format` — apply `ruff format` and `ruff check --fix` in-place
- `hatch run typecheck` — `mypy --strict` over `src` and `tests` (tests have a relaxed override — see Architecture)
- `hatch run check` — `format`, `lint`, then `typecheck`
- `hatch run audit` — `pip-audit --skip-editable` for dependency-vulnerability scan
- `hatch run build-check` — `hatch build` (sdist + wheel) followed by `twine check dist/*`
- `hatch run docs:build` / `hatch run docs:serve` — mkdocs build (with `--strict`) / live preview, in the dedicated `docs` env
- `hatch test` — pytest in the dedicated `hatch-test` env (default Python). Add `--all` for the full matrix or `--cover` for coverage.
- `hatch build` — sdist + wheel via the hatchling backend, output under `dist/`
- `hatch shell` — drop into the default env's interpreter
- `hatch env prune` — remove all hatch-managed environments

Run a single test: `hatch run test tests/test_classifier.py::TestIPv4Classification::test_valid_ipv4` — positional args after the script name are forwarded to pytest via `{args}` in the script definition. With no args, `testpaths = ["tests"]` makes pytest pick up the whole suite.

The `hatch-test` matrix env runs against Python 3.10/3.11/3.12/3.13, matching `requires-python = ">=3.10"`. Ruff is configured with `line-length = 88` and `target-version = "py310"`; the `I` rule (import sorting) is enabled in addition to the default `E` + `F`. Mypy runs in `strict` mode against both `src/` and `tests/`; an override on `tests.*` relaxes `disallow_untyped_defs`/`disallow_incomplete_defs`/`disallow_untyped_decorators` so test methods don't need `-> None` everywhere, while still type-checking calls into the library API. The override matches `tests.*` (dotted module path), which requires `tests/__init__.py` to exist — don't delete it.

The package version is single-sourced from `__version__` in `src/ioc_typing/__init__.py`. `[project]` declares `dynamic = ["version"]` and `[tool.hatch.version] path = ...` tells hatchling where to read it. To bump, edit `__version__` directly or run `hatch version <new>` / `hatch version minor` / etc.

## Architecture

The entire classifier lives in `src/ioc_typing/ioc_classifier.py`. Two design points worth knowing before editing:

1. **Patterns are compiled once in `__init__`.** `_compile_patterns()` builds a dict of `re.Pattern` objects, and `classify()` dispatches via `re.Pattern.fullmatch` (not `match` — `match` with a trailing `$` is permissive about a final newline). The URL regex is assembled from a `url_components` dict (protocol/auth/host/port/path/query/fragment) so individual fragments can be tweaked without rewriting the whole expression. The URL pattern has two top-level alternatives: a full `protocol://...` form, and a schemeless form. The schemeless branch is gated by two lookaheads — `(?!protocol)` (negative) so it doesn't double-match schemed URLs, and `(?=port|path|query|fragment)` (positive) so a bare host doesn't classify as a URL and instead falls through to the domain check.

2. **`classify()` order matters and is deliberate: most-specific → least-specific.** IPv4 → IPv6 → hash (md5/sha1/sha256, by length) → URL → domain → unclassified. Hash patterns are length-based (`{32}`/`{40}`/`{64}` hex), so changing the order or adding a new fixed-length hash without considering collisions will silently mis-classify. URL is checked before domain by specificity convention; in practice the two are mutually exclusive — the schemeless URL branch's positive lookahead requires a port/path/query/fragment, none of which a bare domain ever has.

The domain regex accepts an optional trailing dot (`\.?`) to match the RFC 1034 FQDN form (e.g. `example.com.`). The URL host regex already accepts the same form, so `example.com.` and `example.com.:8080/path` both classify cleanly.

Every classification returns the `ClassificationResult` `TypedDict` (defined alongside `IOCClassifier` in `ioc_classifier.py`): `{"query": str, "determined": bool, "type_pri": str | None, "type_sec": str | None}`. `type_sec` is `"v4"`/`"v6"` for IPs, the hash name for hashes, and `None` for URLs/domains. Unclassified inputs return `determined=False` with both type fields `None`. Non-string inputs surface as `TypeError` from the underlying `re.fullmatch` call (pinned by `TestMiscClassification.test_non_string_input_raises`). Tests in `tests/test_classifier.py` assert this contract per category — extending the classifier means adding both a positive and a negative test class following the existing pattern. `tests/test_classifier_properties.py` adds Hypothesis property tests covering the contract for any IPv4/IPv6 address and any 32/40/64 hex string; if you change classifier semantics in those buckets, update the property tests too. If you add a new key to the result, update the `TypedDict` in the same edit so the public type stays in sync.

## CLI

The package exposes an `ioc-classify` console script via `[project.scripts]` in `pyproject.toml`, pointing at `ioc_typing._cli:main`. The CLI lives in `src/ioc_typing/_cli.py` (note the leading underscore — it's a private module; the only public CLI surface is the entry point itself). It reads one IOC per line from a file or stdin, classifies each via `IOCClassifier`, and emits TSV (default) or JSON Lines. Blank lines and `#`-prefixed lines are skipped. Pipeline-friendly: `BrokenPipeError` is caught so `ioc-classify ... | head` doesn't traceback. CLI behavior is covered by `tests/test_cli.py`; if you change output format or argument shape, update those tests in the same edit.

## Release process

Releases are automated via Trusted Publishing — no API tokens. The flow:

1. Bump `__version__` in `src/ioc_typing/__init__.py` (single source of truth — `[project] dynamic = ["version"]` reads it).
2. In `CHANGELOG.md`, rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and add a fresh empty `[Unreleased]` section above it.
3. Commit, then `git tag -a vX.Y.Z -m "Release X.Y.Z"`.
4. `git push origin main && git push origin vX.Y.Z` — pushing the tag triggers `.github/workflows/release.yml`, which builds sdist+wheel via `build-check`, runs through the `pypi` GitHub environment (OIDC), and publishes via `pypa/gh-action-pypi-publish`.

PyPI does not allow re-uploading the same version even after a yank, so a botched X.Y.Z means skipping to X.Y.Z+1. Verify the workflow succeeded under the **Release** action and the new version appears at https://pypi.org/project/ioc-typing/.

The docs site at https://janwychowaniak.github.io/ioc-typing/ is independent of releases — `.github/workflows/docs.yml` redeploys on any push to `main` that touches `docs/**`, `mkdocs.yml`, `src/**`, or `pyproject.toml`.

## Python compatibility

The project targets Python 3.10+ (`pyproject.toml` sets `requires-python = ">=3.10"`, with classifiers for 3.10/3.11/3.12/3.13). Annotations use PEP 585 builtin generics (`dict[...]`, `re.Pattern[str]`) and PEP 604 unions (`str | None`), both of which require 3.10+.
