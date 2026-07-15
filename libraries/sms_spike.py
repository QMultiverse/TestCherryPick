"""EXPERIMENTAL / WIP — SMS notification spike. DO NOT PROMOTE YET.

This is an unfinished proof-of-concept for an SMS notification channel. It has
no tests, hard-codes a provider, and is not wired into NotificationService.
It intentionally lives on 65-5-Future only and must NOT be cherry-picked to
65-5-Current until it is finished and reviewed.
"""

from __future__ import annotations

# TODO: replace with configured provider + credentials from vault.
_PROVIDER_ENDPOINT = "https://sms.example.com/send"  # placeholder


def send_sms(number: str, message: str) -> dict:
    """Pretend to send an SMS. Not implemented — returns a stub payload."""
    # FIXME: no real transport, no retry, no rate limiting, no validation.
    return {
        "provider": _PROVIDER_ENDPOINT,
        "to": number,
        "message": message,
        "status": "NOT_IMPLEMENTED",
    }
