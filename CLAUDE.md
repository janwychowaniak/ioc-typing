# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`ioc-typing` is a zero-dependency Python library that classifies a string as one of: IPv4/IPv6, domain, URL, or MD5/SHA1/SHA256 hash. The public API is a single class, `IOCClassifier`, exposed from `ioc_typing` (see `src/ioc_typing/__init__.py`).

## Common commands

All workflows go through `tox` (wrapped by `make`):

- `make dev` — create a persistent dev venv at `.venv/` (tox env `dev`, `usedevelop = true`)
- `make test` / `tox` — run pytest with coverage (`pytest -v --cov=src tests`)
- `make lint` — `black --check`, `isort --check-only`, `flake8` over `src tests`
- `make format` — apply `black` and `isort` in-place
- `make check` — `format` then `lint`
- `make build` — `python -m build` + `twine check dist/*`
- `make clean` / `make clean-all` — remove build artefacts (`clean-all` also removes `.venv/`)

Run a single test: `tox -- tests/test_classifier.py::TestIPv4Classification::test_valid_ipv4` (everything after `--` is forwarded to pytest via `{posargs}`).

`tox.ini` runs against `py310, py311, py312, py313` (matching `requires-python = ">=3.10"` in `pyproject.toml`). flake8 is configured for `max-line-length = 88` with `E203` ignored (Black-compatible).

## Architecture

The entire classifier lives in `src/ioc_typing/ioc_classifier.py`. Two design points worth knowing before editing:

1. **Patterns are compiled once in `__init__`.** `_compile_patterns()` builds a dict of `re.Pattern` objects. The URL regex is assembled from a `url_components` dict (protocol/auth/host/port/path/query/fragment) so individual fragments can be tweaked without rewriting the whole expression. The URL pattern has two top-level alternatives: a full `protocol://...` form, and a schemeless form gated by a `(?!protocol)` negative lookahead so bare hosts with a port/path/query/fragment still match.

2. **`classify()` order matters and is deliberate: most-specific → least-specific.** IPv4 → IPv6 → hash (md5/sha1/sha256, by length) → URL → domain → unclassified. Hash patterns are length-based (`{32}`/`{40}`/`{64}` hex), so changing the order or adding a new fixed-length hash without considering collisions will silently mis-classify. URL is checked before domain because every bare domain also matches the schemeless URL branch — keep this ordering.

Every classification returns the same shape: `{"query", "determined", "type_pri", "type_sec"}`. `type_sec` is `"v4"`/`"v6"` for IPs, the hash name for hashes, and `None` for URLs/domains. Unclassified inputs return `determined=False` with both type fields `None`. Tests in `tests/test_classifier.py` assert this contract per category — extending the classifier means adding both a positive and a negative test class following the existing pattern.

## Python compatibility

The project targets Python 3.10+ (`pyproject.toml` sets `requires-python = ">=3.10"`, with classifiers for 3.10/3.11/3.12/3.13). `_create_result` in `ioc_classifier.py` uses PEP 604 `str | None` syntax, which is fine on 3.10+. If you ever need to lower the floor below 3.10, switch those annotations to `Optional[str]` and update both `requires-python` and `tox.ini`'s `envlist`.
