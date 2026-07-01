from engines import generate_transaction_hash, add_hashes, duplicate_hash_groups

REV = {"entity_id": 101, "account_code": "REV4000", "invoice_number": "INV-1001",
       "contract_number": "C-500", "bank_reference_number": "BR-900",
       "counterparty_id": "CUST-01", "transaction_date": "2026-03-15",
       "amount": 250000, "currency": "AUD"}
AR = {**REV, "account_code": "AR1200"}          # same economic txn, different account
OTHER = {**REV, "invoice_number": "INV-9999", "amount": 10}


def test_hash_is_deterministic():
    assert generate_transaction_hash(REV) == generate_transaction_hash(dict(REV))


def test_hash_format():
    h = generate_transaction_hash(REV)
    assert h.startswith("TXN-") and len(h) == 20   # "TXN-" + 16 hex


def test_same_txn_across_accounts_collapses():
    # account_code is not part of the key -> Revenue and AR share one hash
    assert generate_transaction_hash(REV) == generate_transaction_hash(AR)


def test_different_txn_differs():
    assert generate_transaction_hash(REV) != generate_transaction_hash(OTHER)


def test_duplicate_hash_groups_detects_cross_account():
    groups = duplicate_hash_groups([REV, AR, OTHER])
    assert len(groups) == 1
    (rows,) = groups.values()
    assert {r["account_code"] for r in rows} == {"REV4000", "AR1200"}


def test_add_hashes_preserves_rows():
    out = add_hashes([REV, OTHER])
    assert all("transaction_hash" in r for r in out)
    assert out[0]["invoice_number"] == "INV-1001"
