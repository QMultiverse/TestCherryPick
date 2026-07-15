"""Report export helpers (introduced in release 65.5, round 5).

Serialises a run summary into CSV/JSON for downstream dashboards. This is
next-release feature work and is NOT intended for the current release line.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

SUPPORTED_FORMATS = ("json", "csv")


class ReportExporter:
    """Robot keyword library that exports run summaries."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, export_format: str = "json") -> None:
        if export_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported export format: {export_format}")
        self.export_format = export_format

    def export(self, rows: List[Dict[str, Any]]) -> str:
        if self.export_format == "json":
            return json.dumps(rows, sort_keys=True)
        return self._to_csv(rows)

    @staticmethod
    def _to_csv(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        headers = list(rows[0].keys())
        lines = [",".join(headers)]
        for row in rows:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)
