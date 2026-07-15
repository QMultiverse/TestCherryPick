"""Load and expose per-environment configuration.

Reads the nested JSON files under ``config/environments`` and the shared
``config/settings.yaml`` so that Robot suites can resolve environment-specific
values through a single keyword.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import yaml

_CONFIG_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, "config")


class ConfigReader:
    """Robot keyword library that surfaces environment configuration."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, environment: str = "qa") -> None:
        self.environment = environment
        self._config: Dict[str, Any] = {}
        self._settings: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        env_file = os.path.join(_CONFIG_ROOT, "environments", f"{self.environment}.json")
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"No configuration for environment '{self.environment}'")
        with open(env_file, "r", encoding="utf-8") as handle:
            self._config = json.load(handle)

        settings_file = os.path.join(_CONFIG_ROOT, "settings.yaml")
        with open(settings_file, "r", encoding="utf-8") as handle:
            self._settings = yaml.safe_load(handle) or {}

    def get_config(self, dotted_key: str, default: Any = None) -> Any:
        """Return a nested config value using ``a.b.c`` dotted notation."""
        return self._resolve(self._config, dotted_key, default)

    def get_setting(self, dotted_key: str, default: Any = None) -> Any:
        """Return a nested value from the global settings file."""
        return self._resolve(self._settings, dotted_key, default)

    @staticmethod
    def _resolve(source: Dict[str, Any], dotted_key: str, default: Any) -> Any:
        node: Any = source
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node
