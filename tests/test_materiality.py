import pytest
from engines import compute_materiality

BASE = {"benchmark_type": "PBT", "benchmark_amount": 4000000, "percentage": 0.05,
        "adjustment_factor": 1.0, "te_percentage": 0.65, "sad_percentage": 0.05}


def test_formula():
    m = compute_materiality(BASE)
    assert m["pm"] == 200000          # 4,000,000 × 5% × 1.0
    assert m["te"] == 130000          # PM × 65%
    assert m["sad"] == 10000          # PM × 5%


def test_adjustment_factor_applied():
    m = compute_materiality({**BASE, "adjustment_factor": 0.9})
    assert m["pm"] == 180000


def test_invalid_benchmark_raises():
    with pytest.raises(ValueError, match="benchmark_type"):
        compute_materiality({**BASE, "benchmark_type": "EBITDA"})


def test_negative_amount_raises():
    with pytest.raises(ValueError):
        compute_materiality({**BASE, "benchmark_amount": -1})


def test_te_percentage_bounds():
    with pytest.raises(ValueError):
        compute_materiality({**BASE, "te_percentage": 1.5})
