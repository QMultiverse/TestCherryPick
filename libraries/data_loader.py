"""Load environment-agnostic test data from nested JSON files."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_DATA_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, "data", "test_data")


class DataLoader:
    """Robot keyword library for reading test-data fixtures."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def _read(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(_DATA_ROOT, filename)
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def load_users(self) -> List[Dict[str, Any]]:
        return self._read("users.json").get("users", [])

    def load_accounts(self) -> List[Dict[str, Any]]:
        return self._read("accounts.json").get("accounts", [])

    def load_transactions(self) -> List[Dict[str, Any]]:
        return self._read("transactions.json").get("transactions", [])

    def find_user(self, username: str) -> Optional[Dict[str, Any]]:
        for user in self.load_users():
            if user.get("username") == username:
                return user
        return None

    def accounts_for_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        return [acc for acc in self.load_accounts() if acc.get("owner") == owner_id]
