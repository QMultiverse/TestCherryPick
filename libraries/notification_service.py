"""Notification dispatch helpers (introduced in release 65.5, round 3).

Reads the per-environment ``notifications`` config and decides which channels
(email / webhook) are active. Kept transport-agnostic so unit tests can assert
routing without sending anything.
"""

from __future__ import annotations

from typing import Any, Dict, List

VALID_CHANNELS = ("email", "webhook")


class NotificationService:
    """Robot keyword library describing how test notifications are routed."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config: Dict[str, Any] = config or {}

    def enabled_channels(self) -> List[str]:
        """Return the notification channels that are enabled in config."""
        notifications = self.config.get("notifications", {})
        return [
            channel
            for channel in VALID_CHANNELS
            if notifications.get(channel, {}).get("enabled") is True
        ]

    def is_channel_enabled(self, channel: str) -> bool:
        if channel not in VALID_CHANNELS:
            raise ValueError(f"Unknown notification channel: {channel}")
        return channel in self.enabled_channels()

    def format_subject(self, suite: str, passed: int, failed: int) -> str:
        """Build a human-readable notification subject line."""
        status = "PASSED" if failed == 0 else "FAILED"
        return f"[{status}] {suite}: {passed} passed, {failed} failed"
