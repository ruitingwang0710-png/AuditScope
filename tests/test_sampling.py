from engines import select_samples

TE = 126750


def _txn(i, amount, date="2026-05-10", **kw):
    base = {"transaction_id": i, "entity_id": 101, "account_code": "REV4000",
            "invoice_number": f"INV-{i}", "contract_number": f"C-{i}",
            "bank_reference_number": f"BR-{i}", "counterparty_id": "CUST-01",
            "transaction_date": date, "amount": amount, "currency": "AUD"}
    base.update(kw)
    return base


def test_large_item_selected_as_target():
    pop = [_txn(1, 300000), _txn(2, 500)]
    s = select_samples(pop, TE, config={"nss_sample_size": 0})
    targets = [x for x in s if x["sample_type"] == "Target"]
    assert len(targets) == 1
    assert "TE" in targets[0]["selection_reason"]


def test_round_amount_flagged():
    s = select_samples([_txn(1, 5000)], TE, config={"nss_sample_size": 0})
    assert any("round" in x["selection_reason"] for x in s)


def test_year_end_flagged():
    s = select_samples([_txn(1, 100, date="2026-12-31")], TE,
                       config={"nss_sample_size": 0})
    assert any("cut-off" in x["selection_reason"] for x in s)


def test_nss_draws_from_remainder_only():
    # one target (large) + several small items; NSS should pick from the smalls
    pop = [_txn(1, 300000)] + [_txn(i, 100 + i) for i in range(2, 10)]
    s = select_samples(pop, TE, config={"nss_sample_size": 3, "seed": 1})
    nss = [x for x in s if x["sample_type"] == "NSS"]
    assert len(nss) == 3
    # NSS hashes must not overlap target hashes
    target_h = {x["transaction_hash"] for x in s if x["sample_type"] == "Target"}
    assert not (target_h & {x["transaction_hash"] for x in nss})


def test_deterministic_with_seed():
    pop = [_txn(i, 100 + i) for i in range(1, 20)]
    a = select_samples(pop, TE, config={"nss_sample_size": 5, "seed": 42})
    b = select_samples(pop, TE, config={"nss_sample_size": 5, "seed": 42})
    assert [x["transaction_hash"] for x in a] == [x["transaction_hash"] for x in b]


def test_already_tested_becomes_reuse_candidate():
    pop = [_txn(1, 300000)]
    h = select_samples(pop, TE, config={"nss_sample_size": 0})[0]["transaction_hash"]
    s = select_samples(pop, TE, already_tested_hashes={h},
                       config={"nss_sample_size": 0})
    assert s[0]["reuse_status"] == "Reuse Candidate"
