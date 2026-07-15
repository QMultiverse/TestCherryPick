"""Command-line entry point for the report exporter (release 65.5, round 5).

Next-release feature work — a thin CLI wrapper around ReportExporter. NOT for
the current release line.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from report_exporter import SUPPORTED_FORMATS, ReportExporter


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export a run summary.")
    parser.add_argument("input", help="Path to a JSON file containing rows.")
    parser.add_argument("--format", choices=SUPPORTED_FORMATS, default="json")
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as handle:
        rows = json.load(handle)

    exporter = ReportExporter(args.format)
    sys.stdout.write(exporter.export(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
