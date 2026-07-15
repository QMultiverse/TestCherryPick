"""Thin HTTP client wrapper used by the API test suites."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class ApiClient:
    """Robot keyword library that performs HTTP calls against the API."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, base_url: str, timeout_seconds: int = 30, max_retries: int = 3, verify_ssl: bool = True) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._session = requests.Session()
        self._session.headers["Accept"] = "application/json"
        self._token: Optional[str] = None

    def set_auth_token(self, token: str) -> None:
        self._token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _send(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send a request, retrying on transient 5xx/429 responses."""
        last: Optional[requests.Response] = None
        for attempt in range(1, self.max_retries + 1):
            last = self._session.request(
                method, self._url(path), timeout=self.timeout, **kwargs
            )
            if last.status_code not in (429, 500, 502, 503, 504):
                return last
        return last

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._session.get(
            self._url(path), params=params, timeout=self.timeout, verify=self.verify_ssl
        )

    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._send("POST", path, json=payload)
