"""
engines/materiality.py - Materiality calculation (Module 2)
===========================================================
Formulas (see DESIGN_DOC section 4):
    PM  = benchmark_amount x percentage x adjustment_factor
    TE  = PM x te_percentage
    SAD = PM x sad_percentage
Pure function - no DB/UI dependencies, so it is easy to unit-test.
"""
from __future__ import annotations

from typing import Any

VALID_BENCHMARKS = {"PBT", "Revenue", "Assets", "Equity"}


def compute_materiality(inputs: dict[str, Any]) -> dict[str, Any]:
    """
    inputs must contain: benchmark_type, benchmark_amount, percentage,
                         adjustment_factor, te_percentage, sad_percentage
    Returns a dict with pm/te/sad plus the echoed inputs.
    """
    btype = str(inputs.get("benchmark_type", "")).strip()
    if btype not in VALID_BENCHMARKS:
        raise ValueError(f"Invalid benchmark_type: {btype!r}, expected one of {sorted(VALID_BENCHMARKS)}")

    amount = float(inputs["benchmark_amount"])
    pct = float(inputs["percentage"])
    adj = float(inputs.get("adjustment_factor", 1.0))
    te_pct = float(inputs["te_percentage"])
    sad_pct = float(inputs["sad_percentage"])

    for name, v in [("benchmark_amount", amount), ("percentage", pct),
                    ("adjustment_factor", adj), ("te_percentage", te_pct),
                    ("sad_percentage", sad_pct)]:
        if v < 0:
            raise ValueError(f"{name} cannot be negative: {v}")
    if not (0 < te_pct <= 1):
        raise ValueError(f"te_percentage must be in (0, 1]: {te_pct}")
    if not (0 <= sad_pct <= 1):
        raise ValueError(f"sad_percentage must be in [0, 1]: {sad_pct}")

    pm = amount * pct * adj
    te = pm * te_pct
    sad = pm * sad_pct
    return {
        "benchmark_type": btype,
        "benchmark_amount": round(amount, 2),
        "percentage": pct,
        "adjustment_factor": adj,
        "te_percentage": te_pct,
        "sad_percentage": sad_pct,
        "pm": round(pm, 2),
        "te": round(te, 2),
        "sad": round(sad, 2),
        "reason_for_revision": inputs.get("reason_for_revision", ""),
    }
