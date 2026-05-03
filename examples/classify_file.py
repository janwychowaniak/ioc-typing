#!/usr/bin/env python3
"""Classify IOCs read from a file (one per line) and emit TSV output.

Usage:
    python examples/classify_file.py path/to/iocs.txt

Lines are stripped before classification; blank lines and lines starting
with ``#`` are skipped. Output columns: ``query``, ``determined``,
``type_pri``, ``type_sec``. ``-`` is used for ``None`` type fields so
the TSV stays cut/awk-friendly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ioc_typing import IOCClassifier


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="File with one IOC per line")
    args = parser.parse_args()

    classifier = IOCClassifier()
    print("query\tdetermined\ttype_pri\ttype_sec")

    try:
        with args.path.open(encoding="utf-8") as fp:
            for raw in fp:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                r = classifier.classify(line)
                print(
                    f"{r['query']}\t{r['determined']}\t"
                    f"{r['type_pri'] or '-'}\t{r['type_sec'] or '-'}"
                )
    except FileNotFoundError:
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
