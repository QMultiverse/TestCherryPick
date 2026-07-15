"""Structured log formatting helpers (introduced in release 65.5, round 4).

Turns test events into single-line JSON records so CI log processors can index
them. Transport-agnostic: callers decide where the string goes.
"""

from __future__ import annotations

import json
from typing import Any, Dict

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class LogFormatter:
    """Robot keyword library that renders structured log lines."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, suite: str = "unknown") -> None:
        self.suite = suite

    def format_event(self, level: str, message: str, **fields: Any) -> str:
        """Return a compact JSON log line for a single event."""
        level = level.upper()
        if level not in LEVELS:
            raise ValueError(f"Unknown log level: {level}")
        record: Dict[str, Any] = {
            "suite": self.suite,
            "level": level,
            "message": message,
        }
        record.update(fields)
        return json.dumps(record, sort_keys=True, separators=(",", ":"))

    def format_result(self, test: str, status: str, duration_ms: int) -> str:
        return self.format_event(
            "INFO" if status == "PASS" else "ERROR",
            f"test {status.lower()}",
            test=test,
            status=status,
            duration_ms=duration_ms,
        )
