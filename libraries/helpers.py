"""Consolidated helper functions (release 65.5, round 6).

Supersedes the older ``libraries/utils.py`` module: it provides the same
helpers plus hardened input validation. New code should import from here;
``utils.py`` is removed in a follow-up commit.
"""

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


def mask_secret(value: str, visible: int = 2) -> str:
    """Mask all but the last ``visible`` characters of a secret.

    Hardened vs the old ``utils.mask_secret``: validates its inputs instead of
    silently mishandling them.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        raise TypeError("mask_secret expects a string value")
    if visible < 0:
        raise ValueError("visible must be non-negative")
    if not value:
        return ""
    if len(value) <= visible:
        return "*" * len(value)
    return "*" * (len(value) - visible) + value[-visible:]
