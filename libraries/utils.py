"""Small assorted helpers shared by libraries and suites."""

from __future__ import annotations

from typing import Any, Dict


def deep_get(source: Dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    """Return a nested dict value using ``a.b.c`` dotted notation."""
    node: Any = source
    for part in dotted_key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node


def mask_secret(value: str, visible: int = 4) -> str:
    """Mask all but the last ``visible`` characters of a secret."""
    if not value:
        return ""
    if len(value) <= visible:
        return "*" * len(value)
    return "*" * (len(value) - visible) + value[-visible:]
