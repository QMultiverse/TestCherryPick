"""Reusable retry/back-off policy (introduced in release 65.5, round 2).

A small, dependency-free helper that computes exponential back-off delays and
decides whether another attempt should be made. Used by the API client and the
retry test suite.
"""

from __future__ import annotations

from typing import Iterable

# HTTP status codes that are considered worth retrying.
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})


class RetryPolicy:
    """Robot keyword library describing how failed requests are retried."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, max_attempts: int = 3, base_delay_ms: int = 200) -> None:
        self.max_attempts = max_attempts
        self.base_delay_ms = base_delay_ms

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Return True if another attempt is allowed for this status code."""
        if attempt >= self.max_attempts:
            return False
        return status_code in RETRYABLE_STATUS

    def backoff_delay_ms(self, attempt: int) -> int:
        """Exponential back-off: base * 2**(attempt-1), capped at 5s."""
        if attempt < 1:
            attempt = 1
        return min(self.base_delay_ms * (2 ** (attempt - 1)), 5000)

    def delays(self) -> Iterable[int]:
        """Yield the back-off delay for each attempt in the policy."""
        return [self.backoff_delay_ms(a) for a in range(1, self.max_attempts + 1)]
