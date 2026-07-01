"""
engines/hashing.py - Unique Transaction ID (Module 6)
=====================================================
Generates a stable, deterministic hash so the same economic transaction is
recognised as identical wherever it appears (different ledgers / accounts /
tests). This is the technical backbone of de-duplication and evidence reuse.

V1 uses EXACT match on the key fields below. Fuzzy match (same supplier + close
date + same amount + similar invoice) is a V3 extension.
"""
from __future__ import annotations

import hashlib
from typing import Any

# Key fields that identify the economic transaction (NOTE: account_code is
# deliberately excluded, so the same transaction posted to two accounts - e.g.
# a sale hitting both Revenue and AR - collapses to one hash).
HASH_FIELDS = [
    "entity_id", "invoice_number", "contract_number", "bank_reference_number",
    "counterparty_id", "transaction_date", "amount", "currency",
]


def _norm(value: Any) -> str:
    """Normalise a field so trivial format differences do not change the hash."""
    if value is None:
        return ""
    s = str(value).strip()
    return s.casefold()


def generate_transaction_hash(row: dict[str, Any]) -> str:
    key = "|".join(_norm(row.get(f)) for f in HASH_FIELDS)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16].upper()
    return f"TXN-{digest}"


def add_hashes(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of each transaction with a transaction_hash added."""
    out = []
    for t in transactions:
        row = dict(t)
        row["transaction_hash"] = generate_transaction_hash(t)
        out.append(row)
    return out


def duplicate_hash_groups(transactions: list[dict[str, Any]]
                          ) -> dict[str, list[dict[str, Any]]]:
    """
    Group transactions by hash and return only groups with more than one row -
    i.e. the same economic transaction recorded multiple times (e.g. across
    Revenue and AR). Useful for evidence reuse and duplicate detection.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for t in add_hashes(transactions):
        groups.setdefault(t["transaction_hash"], []).append(t)
    return {h: rows for h, rows in groups.items() if len(rows) > 1}
