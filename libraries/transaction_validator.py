"""Validation helpers for transaction records (introduced in release 65.5).

Provides Robot keywords that assert structural and business rules on the
transaction fixtures and API responses.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

VALID_TYPES = {"debit", "credit"}
VALID_STATUSES = {"pending", "settled", "reversed"}


class TransactionValidator:
    """Robot keyword library that validates transaction payloads."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Assert a single transaction has the required shape and values."""
        required = {"txn_id", "account_id", "type", "amount", "currency", "status"}
        missing = required - set(transaction)
        if missing:
            raise AssertionError(f"Transaction missing fields: {sorted(missing)}")
        if transaction["type"] not in VALID_TYPES:
            raise AssertionError(f"Invalid transaction type: {transaction['type']}")
        if transaction["status"] not in VALID_STATUSES:
            raise AssertionError(f"Invalid transaction status: {transaction['status']}")
        if float(transaction["amount"]) <= 0:
            raise AssertionError("Transaction amount must be positive")
        return True

    def validate_all(self, transactions: Iterable[Dict[str, Any]]) -> int:
        """Validate every transaction and return the count checked."""
        count = 0
        for txn in transactions:
            self.validate_transaction(txn)
            count += 1
        return count

    def net_amount(self, transactions: Iterable[Dict[str, Any]]) -> float:
        """Return credits minus debits across the supplied transactions."""
        total = 0.0
        for txn in transactions:
            amount = float(txn["amount"])
            total += amount if txn["type"] == "credit" else -amount
        return round(total, 2)
