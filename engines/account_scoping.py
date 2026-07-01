"""
engines/account_scoping.py — 科目范围判断(Module 4)
=====================================================
对每个 in-scope 主体的 TB 逐科目判定是否测试、测试类型与理由。
决策由 重要性(TE/SAD) × 风险评级 × 科目类型 共同决定。
"""
from __future__ import annotations

from typing import Any

# 交易性科目才适合叠加 NSS(非统计抽样);资产负债存量类偏 target/specific
TRANSACTIONAL_TYPES = {"Revenue", "Expense", "Asset", "Liability"}


def score_accounts(accounts: list[dict[str, Any]], te: float, sad: float
                   ) -> list[dict[str, Any]]:
    """
    accounts: 每个 dict 含 account_name, account_type, balance, movement, risk_rating。
    te / sad: 当前生效重要性阈值。
    返回:加 testing_required / testing_type / testing_reason。
    """
    out = []
    for a in accounts:
        atype = str(a.get("account_type", "")).strip()
        balance = abs(float(a.get("balance", 0) or 0))
        movement = abs(float(a.get("movement", 0) or 0))
        risk = str(a.get("risk_rating", "")).strip().lower()
        exceeds_te = balance > te or movement > te
        transactional = atype in TRANSACTIONAL_TYPES

        if balance <= sad and risk != "high":
            required, ttype = 0, "None"
            reason = f"余额 {balance:,.0f} ≤ SAD {sad:,.0f} 且风险不高,无需详细测试"
        elif risk == "high":
            required = 1
            if exceeds_te:
                ttype = "Target + NSS" if transactional else "Target"
                reason = f"高风险且超过 TE {te:,.0f},需重点测试" + (" + 抽样" if transactional else "")
            else:
                ttype = "Specific"
                reason = f"高风险(余额 {balance:,.0f} 未超 TE),做针对性专项测试"
        elif exceeds_te:
            required = 1
            ttype = "Target + NSS" if transactional else "Target"
            reason = (f"余额/变动超过 TE {te:,.0f}"
                      + (",交易性科目 → 定向 + 非统计抽样" if transactional else ",→ 定向测试"))
        else:
            required = 1
            ttype = "NSS"
            reason = f"介于 SAD 与 TE 之间,做非统计抽样覆盖"

        row = dict(a)
        row["testing_required"] = required
        row["testing_type"] = ttype
        row["testing_reason"] = reason
        out.append(row)
    return out
