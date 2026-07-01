"""
engines/sampling.py - Sampling engine (Module 5)
================================================
For a transaction population within a testable account, selects:

  A. Target items  - directed selection of inherently risky / material items:
       - amount >= TE (large / material)
       - round amounts over a threshold (potential fabrication)
       - month-end / year-end postings (cut-off risk)
       (related-party & red-flag hooks are added in later weeks)

  B. NSS items     - a fixed-size non-statistical sample drawn from the
       remaining population (excluding target-selected and already-reusable
       items).

Every selected item carries a selection_reason. Selection is deterministic
(seeded) so results are reproducible. Pure functions - no DB/UI dependencies.
"""
from __future__ import annotations

import random
from typing import Any

from .hashing import generate_transaction_hash

DEFAULT_CONFIG = {
    "nss_sample_size": 5,       # fixed NSS count per account
    "round_amount_min": 1000,   # round-amount rule only applies above this
    "seed": 2026,
}
MONTH_END_DAYS = {"28", "29", "30", "31"}


def _is_round(amount: float, floor: float) -> bool:
    return amount > floor and amount % 1000 == 0


def _is_period_end(date_str: str) -> bool:
    # expects YYYY-MM-DD...; treat day-of-month in {28..31} as period-end proxy,
    # and December as year-end.
    s = str(date_str)
    if len(s) < 10:
        return False
    day = s[8:10]
    return day in MONTH_END_DAYS


def _target_reason(amount, te, date_str, round_floor) -> str | None:
    reasons = []
    if amount >= te:
        reasons.append(f"amount {amount:,.0f} >= TE {te:,.0f}")
    if _is_round(amount, round_floor):
        reasons.append("round amount (potential fabrication)")
    if _is_period_end(date_str):
        reasons.append("month/year-end posting (cut-off risk)")
    return "; ".join(reasons) if reasons else None


def select_samples(transactions: list[dict[str, Any]], te: float,
                   already_tested_hashes: set[str] | None = None,
                   config: dict | None = None) -> list[dict[str, Any]]:
    """
    transactions: population for ONE account (each dict has amount,
                  transaction_date, and hashable key fields).
    te: performance materiality threshold.
    already_tested_hashes: hashes already tested (become reuse candidates,
                  excluded from fresh NSS).
    Returns a list of sample dicts:
        transaction_hash, sample_type, selection_reason,
        testing_status, reuse_status
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    tested = already_tested_hashes or set()
    rng = random.Random(cfg["seed"])

    # ensure hashes present
    pop = []
    for t in transactions:
        row = dict(t)
        row["transaction_hash"] = row.get("transaction_hash") or generate_transaction_hash(t)
        pop.append(row)

    samples: list[dict[str, Any]] = []
    target_hashes: set[str] = set()

    # A. Target
    for t in pop:
        amount = abs(float(t.get("amount", 0) or 0))
        reason = _target_reason(amount, te, t.get("transaction_date", ""),
                                cfg["round_amount_min"])
        if reason:
            h = t["transaction_hash"]
            target_hashes.add(h)
            samples.append({
                "transaction_hash": h,
                "sample_type": "Target",
                "selection_reason": reason,
                "testing_status": "Not tested",
                "reuse_status": "Reuse Candidate" if h in tested else "-",
            })

    # B. NSS on the remainder (exclude target-selected and already-tested)
    remainder = [t for t in pop
                 if t["transaction_hash"] not in target_hashes
                 and t["transaction_hash"] not in tested]
    # de-duplicate remainder by hash (same economic txn counted once)
    seen: set[str] = set()
    unique_remainder = []
    for t in remainder:
        if t["transaction_hash"] not in seen:
            seen.add(t["transaction_hash"])
            unique_remainder.append(t)

    n = min(cfg["nss_sample_size"], len(unique_remainder))
    for t in rng.sample(unique_remainder, n) if n else []:
        samples.append({
            "transaction_hash": t["transaction_hash"],
            "sample_type": "NSS",
            "selection_reason": "random non-statistical sample",
            "testing_status": "Not tested",
            "reuse_status": "-",
        })

    return samples
