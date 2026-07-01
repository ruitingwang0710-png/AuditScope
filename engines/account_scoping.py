"""
engines/account_scoping.py - Account scoping (Module 4)
=======================================================
For each in-scope entity's trial balance, decides per account whether testing is
required, the testing type and the rationale. Decisions are driven by
materiality (TE/SAD) x risk rating x account type.
"""
from __future__ import annotations

from typing import Any

# Only transactional accounts are suitable for NSS (non-statistical sampling);
# balance-sheet stock accounts lean towards target / specific testing.
TRANSACTIONAL_TYPES = {"Revenue", "Expense", "Asset", "Liability"}


def score_accounts(accounts: list[dict[str, Any]], te: float, sad: float
                   ) -> list[dict[str, Any]]:
    """
    accounts: each dict has account_name, account_type, balance, movement, risk_rating.
    te / sad: currently active materiality thresholds.
    Returns each dict extended with testing_required / testing_type / testing_reason.
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
            reason = (f"Balance {balance:,.0f} <= SAD {sad:,.0f} and risk not high; "
                      f"no detailed testing required")
        elif risk == "high":
            required = 1
            if exceeds_te:
                ttype = "Target + NSS" if transactional else "Target"
                reason = (f"High risk and exceeds TE {te:,.0f}; focused testing"
                          + (" + sampling" if transactional else ""))
            else:
                ttype = "Specific"
                reason = (f"High risk (balance {balance:,.0f} below TE); "
                          f"perform specific targeted procedures")
        elif exceeds_te:
            required = 1
            ttype = "Target + NSS" if transactional else "Target"
            reason = (f"Balance/movement exceeds TE {te:,.0f}"
                      + ("; transactional account -> target + non-statistical sampling"
                         if transactional else "; -> target testing"))
        else:
            required = 1
            ttype = "NSS"
            reason = "Between SAD and TE; cover via non-statistical sampling"

        row = dict(a)
        row["testing_required"] = required
        row["testing_type"] = ttype
        row["testing_reason"] = reason
        out.append(row)
    return out
