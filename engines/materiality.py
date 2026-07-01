"""
engines/materiality.py — 重要性计算(Module 2)
===============================================
公式(见 DESIGN_DOC 第 4 节):
    PM  = benchmark_amount × percentage × adjustment_factor
    TE  = PM × te_percentage
    SAD = PM × sad_percentage
纯函数,不碰 DB/UI,方便单测。
"""
from __future__ import annotations

from typing import Any

VALID_BENCHMARKS = {"PBT", "Revenue", "Assets", "Equity"}


def compute_materiality(inputs: dict[str, Any]) -> dict[str, Any]:
    """
    inputs 需含:benchmark_type, benchmark_amount, percentage,
                adjustment_factor, te_percentage, sad_percentage
    返回:含 pm/te/sad 及回显输入的 dict。
    """
    btype = str(inputs.get("benchmark_type", "")).strip()
    if btype not in VALID_BENCHMARKS:
        raise ValueError(f"benchmark_type 非法: {btype!r},应为 {sorted(VALID_BENCHMARKS)}")

    amount = float(inputs["benchmark_amount"])
    pct = float(inputs["percentage"])
    adj = float(inputs.get("adjustment_factor", 1.0))
    te_pct = float(inputs["te_percentage"])
    sad_pct = float(inputs["sad_percentage"])

    for name, v in [("benchmark_amount", amount), ("percentage", pct),
                    ("adjustment_factor", adj), ("te_percentage", te_pct),
                    ("sad_percentage", sad_pct)]:
        if v < 0:
            raise ValueError(f"{name} 不能为负: {v}")
    if not (0 < te_pct <= 1):
        raise ValueError(f"te_percentage 应在 (0,1]: {te_pct}")
    if not (0 <= sad_pct <= 1):
        raise ValueError(f"sad_percentage 应在 [0,1]: {sad_pct}")

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
