"""Thin HTTP client wrapper used by the API test suites."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class ApiClient:
    """Robot keyword library that performs HTTP calls against the API."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, base_url: str, timeout_seconds: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self._session = requests.Session()
        self._token: Optional[str] = None

    def set_auth_token(self, token: str) -> None:
        self._token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._session.get(self._url(path), params=params, timeout=self.timeout)

    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._session.post(self._url(path), json=payload, timeout=self.timeout)
