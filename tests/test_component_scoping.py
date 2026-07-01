from engines import score_components

COMPS = [
    {"entity_id": 1, "entity_name": "Big",    "revenue": 42_000_000, "pbt": 3_100_000, "risk_rating": "Medium"},
    {"entity_id": 2, "entity_name": "Cloud",  "revenue": 18_000_000, "pbt": 900_000,   "risk_rating": "High"},
    {"entity_id": 3, "entity_name": "Mid",    "revenue": 9_000_000,  "pbt": 350_000,   "risk_rating": "Medium"},
    {"entity_id": 4, "entity_name": "SmallHi","revenue": 3_000_000,  "pbt": 120_000,   "risk_rating": "High"},
    {"entity_id": 5, "entity_name": "Tiny",   "revenue": 1_500_000,  "pbt": 60_000,    "risk_rating": "Low"},
]


def _by(rows, name):
    return next(r for r in rows if r["entity_name"] == name)


def test_full_scope_when_contribution_over_15pct():
    r = _by(score_components(COMPS), "Big")
    assert r["scope_decision"] == "Full Scope"
    assert r["contribution_pct"] > 15


def test_high_risk_gets_specific_even_if_small():
    r = _by(score_components(COMPS), "SmallHi")   # ~4% but High risk
    assert r["scope_decision"] == "Specific Scope"


def test_mid_contribution_specific():
    r = _by(score_components(COMPS), "Mid")       # ~12%
    assert r["scope_decision"] == "Specific Scope"


def test_small_low_risk_analytical():
    r = _by(score_components(COMPS), "Tiny")
    assert r["scope_decision"] == "Analytical Review"


def test_every_row_has_reason():
    assert all(r["scope_reason"] for r in score_components(COMPS))
