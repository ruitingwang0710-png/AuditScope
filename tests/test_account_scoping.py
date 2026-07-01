from engines import score_accounts

TE, SAD = 130000, 10000


def _one(acc):
    return score_accounts([acc], TE, SAD)[0]


def test_below_sad_no_testing():
    r = _one({"account_id": 1, "account_name": "Office", "account_type": "Expense",
              "balance": 8000, "movement": 8000, "risk_rating": "Low"})
    assert r["testing_required"] == 0
    assert r["testing_type"] == "None"


def test_revenue_over_te_target_plus_nss():
    r = _one({"account_id": 2, "account_name": "Revenue", "account_type": "Revenue",
              "balance": 8_000_000, "movement": 8_000_000, "risk_rating": "High"})
    assert r["testing_required"] == 1
    assert r["testing_type"] == "Target + NSS"


def test_high_risk_low_balance_specific():
    r = _one({"account_id": 3, "account_name": "Tax", "account_type": "Liability",
              "balance": 80000, "movement": 80000, "risk_rating": "High"})
    assert r["testing_type"] == "Specific"


def test_between_sad_and_te_nss():
    r = _one({"account_id": 4, "account_name": "Prepaid", "account_type": "Asset",
              "balance": 50000, "movement": 20000, "risk_rating": "Low"})
    assert r["testing_type"] == "NSS"


def test_non_transactional_over_te_target_only():
    r = _one({"account_id": 5, "account_name": "Goodwill", "account_type": "Intangible",
              "balance": 5_000_000, "movement": 0, "risk_rating": "Medium"})
    assert r["testing_type"] == "Target"
