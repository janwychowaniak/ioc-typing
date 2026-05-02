"""Command-line interface for the ioc-typing classifier.

Reads one IOC per line from a file (or stdin) and emits classification
results as TSV (default) or JSON Lines. Blank lines and lines starting
with ``#`` are skipped so input files can be commented.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from .ioc_classifier import ClassificationResult, IOCClassifier


def _filter_lines(source: Iterable[str]) -> Iterator[str]:
    for raw in source:
        line = raw.strip()
        if line and not line.startswith("#"):
            yield line


def _iter_lines(path: str | None) -> Iterator[str]:
    if path is None or path == "-":
        yield from _filter_lines(sys.stdin)
    else:
        with Path(path).open(encoding="utf-8") as fp:
            yield from _filter_lines(fp)


def _emit_tsv(results: Iterable[ClassificationResult]) -> None:
    print("query\tdetermined\ttype_pri\ttype_sec")
    for r in results:
        print(
            f"{r['query']}\t{r['determined']}\t"
            f"{r['type_pri'] or '-'}\t{r['type_sec'] or '-'}"
        )


def _emit_jsonl(results: Iterable[ClassificationResult]) -> None:
    for r in results:
        print(json.dumps(r))


def _suppress_remaining_output() -> None:
    # Redirect stdout to /dev/null so the interpreter's exit-time flush
    # doesn't re-raise BrokenPipeError after we've handled it. See
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ioc-classify",
        description="Classify IOCs (one per line) from a file or stdin.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File with one IOC per line. Use '-' or omit for stdin.",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "json"),
        default="tsv",
        help="Output format (default: tsv; json emits JSON Lines).",
    )
    args = parser.parse_args(argv)

    classifier = IOCClassifier()
    results = (classifier.classify(line) for line in _iter_lines(args.path))

    try:
        if args.format == "tsv":
            _emit_tsv(results)
        else:
            _emit_jsonl(results)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        _suppress_remaining_output()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
