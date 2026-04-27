# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`ioc-typing` is a zero-dependency Python library that classifies a string as one of: IPv4/IPv6, domain, URL, or MD5/SHA1/SHA256 hash. The public API is `IOCClassifier` plus the `ClassificationResult` `TypedDict`, both exposed from `ioc_typing` (see `src/ioc_typing/__init__.py`). The package ships a `py.typed` marker so downstream type checkers consume the inline annotations.

## Common commands

All workflows go through `tox` (wrapped by `make`):

- `make dev` — create a persistent dev venv at `.venv/` (tox env `dev`, `usedevelop = true`)
- `make test` / `tox` — run pytest with coverage (`pytest -v --cov=src tests`)
- `make lint` — `ruff format --check` and `ruff check` over `src tests`
- `make format` — apply `ruff format` and `ruff check --fix` in-place
- `make typecheck` — `mypy --strict` over `src` (config in `pyproject.toml`)
- `make check` — `format`, `lint`, then `typecheck`
- `make build` — `python -m build` (hatchling backend) + `twine check dist/*`
- `make clean` / `make clean-all` — remove build artefacts (`clean-all` also removes `.venv/`)

Run a single test: `tox -- tests/test_classifier.py::TestIPv4Classification::test_valid_ipv4` (everything after `--` is forwarded to pytest via `{posargs}`).

`tox.ini` runs against `py310, py311, py312, py313` (matching `requires-python = ">=3.10"` in `pyproject.toml`). Ruff is configured with `line-length = 88` and `target-version = "py310"`; the `I` rule (import sorting) is enabled in addition to the default `E` + `F`. Mypy runs in `strict` mode against `src/` only (tests are excluded — pytest fixtures are inherently dynamic and the upside is small for this codebase).

## Architecture

The entire classifier lives in `src/ioc_typing/ioc_classifier.py`. Two design points worth knowing before editing:

1. **Patterns are compiled once in `__init__`.** `_compile_patterns()` builds a dict of `re.Pattern` objects, and `classify()` dispatches via `re.Pattern.fullmatch` (not `match` — `match` with a trailing `$` is permissive about a final newline). The URL regex is assembled from a `url_components` dict (protocol/auth/host/port/path/query/fragment) so individual fragments can be tweaked without rewriting the whole expression. The URL pattern has two top-level alternatives: a full `protocol://...` form, and a schemeless form. The schemeless branch is gated by two lookaheads — `(?!protocol)` (negative) so it doesn't double-match schemed URLs, and `(?=port|path|query|fragment)` (positive) so a bare host doesn't classify as a URL and instead falls through to the domain check.

2. **`classify()` order matters and is deliberate: most-specific → least-specific.** IPv4 → IPv6 → hash (md5/sha1/sha256, by length) → URL → domain → unclassified. Hash patterns are length-based (`{32}`/`{40}`/`{64}` hex), so changing the order or adding a new fixed-length hash without considering collisions will silently mis-classify. URL is checked before domain by specificity convention; in practice the two are mutually exclusive — the schemeless URL branch's positive lookahead requires a port/path/query/fragment, none of which a bare domain ever has.

The domain regex accepts an optional trailing dot (`\.?`) to match the RFC 1034 FQDN form (e.g. `example.com.`). The URL host regex already accepts the same form, so `example.com.` and `example.com.:8080/path` both classify cleanly.

Every classification returns the `ClassificationResult` `TypedDict` (defined alongside `IOCClassifier` in `ioc_classifier.py`): `{"query": str, "determined": bool, "type_pri": str | None, "type_sec": str | None}`. `type_sec` is `"v4"`/`"v6"` for IPs, the hash name for hashes, and `None` for URLs/domains. Unclassified inputs return `determined=False` with both type fields `None`. Non-string inputs surface as `TypeError` from the underlying `re.fullmatch` call (pinned by `TestMiscClassification.test_non_string_input_raises`). Tests in `tests/test_classifier.py` assert this contract per category — extending the classifier means adding both a positive and a negative test class following the existing pattern. If you add a new key to the result, update the `TypedDict` in the same edit so the public type stays in sync.

## Python compatibility

The project targets Python 3.10+ (`pyproject.toml` sets `requires-python = ">=3.10"`, with classifiers for 3.10/3.11/3.12/3.13). Annotations use PEP 585 builtin generics (`dict[...]`, `re.Pattern[str]`) and PEP 604 unions (`str | None`), both of which require 3.10+. If you ever need to lower the floor below 3.10, switch those to `Dict[...]`/`Optional[...]` from `typing` and update both `requires-python` and `tox.ini`'s `envlist`.
