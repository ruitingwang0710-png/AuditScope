"""
engines/component_scoping.py - Group component scoping (Module 3)
=================================================================
Classifies each group entity as Full / Specific / Analytical scope based on its
contribution to the group (computed on both revenue and PBT, taking the more
conservative = higher value) combined with its risk rating. Thresholds are
configurable.
"""
from __future__ import annotations

from typing import Any

DEFAULT_THRESHOLDS = {
    "full_scope_pct": 15.0,       # contribution > 15% -> Full
    "specific_low_pct": 5.0,      # 5%-15% -> Specific
}


def _pct(part: float, total: float) -> float:
    return (part / total * 100.0) if total else 0.0


def score_components(components: list[dict[str, Any]],
                     thresholds: dict | None = None) -> list[dict[str, Any]]:
    """
    components: each dict has entity_name, revenue, pbt, risk_rating (may also
                carry entity_id, etc.).
    Returns each dict extended with contribution_pct / scope_decision / scope_reason.
    """
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    total_rev = sum(float(c.get("revenue", 0) or 0) for c in components)
    total_pbt = sum(abs(float(c.get("pbt", 0) or 0)) for c in components)

    out = []
    for c in components:
        rev_pct = _pct(float(c.get("revenue", 0) or 0), total_rev)
        pbt_pct = _pct(abs(float(c.get("pbt", 0) or 0)), total_pbt)
        contribution = max(rev_pct, pbt_pct)   # conservative: take the higher
        risk = str(c.get("risk_rating", "")).strip().lower()

        if rev_pct > t["full_scope_pct"] or pbt_pct > t["full_scope_pct"]:
            scope = "Full Scope"
            reason = (f"Contribution {contribution:.1f}% exceeds {t['full_scope_pct']:.0f}% "
                      f"(revenue {rev_pct:.1f}% / PBT {pbt_pct:.1f}%); full-scope audit required")
        elif risk == "high":
            scope = "Specific Scope"
            reason = (f"High risk rating (contribution {contribution:.1f}%); "
                      f"specific-scope audit required")
        elif t["specific_low_pct"] <= contribution <= t["full_scope_pct"]:
            scope = "Specific Scope"
            reason = (f"Contribution {contribution:.1f}% falls within the "
                      f"{t['specific_low_pct']:.0f}%-{t['full_scope_pct']:.0f}% range")
        else:
            scope = "Analytical Review"
            reason = (f"Contribution {contribution:.1f}% below {t['specific_low_pct']:.0f}% "
                      f"and risk not high; analytical review is sufficient")

        row = dict(c)
        row["contribution_pct"] = round(contribution, 1)
        row["revenue_pct"] = round(rev_pct, 1)
        row["pbt_pct"] = round(pbt_pct, 1)
        row["scope_decision"] = scope
        row["scope_reason"] = reason
        out.append(row)
    return out
