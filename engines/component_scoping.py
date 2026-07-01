"""
engines/component_scoping.py — 集团主体范围判断(Module 3)
==========================================================
按每个主体对集团的贡献度(revenue 与 pbt 各算一套,取更保守=更高者)
结合风险评级,判定 Full / Specific / Analytical Scope。阈值可配置。
"""
from __future__ import annotations

from typing import Any

DEFAULT_THRESHOLDS = {
    "full_scope_pct": 15.0,       # 贡献度 > 15% → Full
    "specific_low_pct": 5.0,      # 5%–15% → Specific
}


def _pct(part: float, total: float) -> float:
    return (part / total * 100.0) if total else 0.0


def score_components(components: list[dict[str, Any]],
                     thresholds: dict | None = None) -> list[dict[str, Any]]:
    """
    components: 每个 dict 含 entity_name, revenue, pbt, risk_rating(可含 entity_id 等)。
    返回:在原 dict 基础上加 contribution_pct / scope_decision / scope_reason。
    """
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    total_rev = sum(float(c.get("revenue", 0) or 0) for c in components)
    total_pbt = sum(abs(float(c.get("pbt", 0) or 0)) for c in components)

    out = []
    for c in components:
        rev_pct = _pct(float(c.get("revenue", 0) or 0), total_rev)
        pbt_pct = _pct(abs(float(c.get("pbt", 0) or 0)), total_pbt)
        contribution = max(rev_pct, pbt_pct)   # 更保守:取较高者
        risk = str(c.get("risk_rating", "")).strip().lower()

        if rev_pct > t["full_scope_pct"] or pbt_pct > t["full_scope_pct"]:
            scope = "Full Scope"
            reason = (f"贡献度 {contribution:.1f}% 超过 {t['full_scope_pct']:.0f}% "
                      f"(收入 {rev_pct:.1f}% / 利润 {pbt_pct:.1f}%),需全范围审计")
        elif risk == "high":
            scope = "Specific Scope"
            reason = f"风险评级为 High(贡献度 {contribution:.1f}%),需针对性范围审计"
        elif t["specific_low_pct"] <= contribution <= t["full_scope_pct"]:
            scope = "Specific Scope"
            reason = (f"贡献度 {contribution:.1f}% 处于 "
                      f"{t['specific_low_pct']:.0f}%–{t['full_scope_pct']:.0f}% 区间")
        else:
            scope = "Analytical Review"
            reason = (f"贡献度 {contribution:.1f}% 低于 {t['specific_low_pct']:.0f}% "
                      f"且风险不高,做分析性复核即可")

        row = dict(c)
        row["contribution_pct"] = round(contribution, 1)
        row["revenue_pct"] = round(rev_pct, 1)
        row["pbt_pct"] = round(pbt_pct, 1)
        row["scope_decision"] = scope
        row["scope_reason"] = reason
        out.append(row)
    return out
