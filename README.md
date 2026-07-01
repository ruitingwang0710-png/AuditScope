# AuditScope

**Group Audit Sampling, Evidence Reuse & Red-Flag Analytics System**

> **Status:** Week 1 design-doc package complete; **Weeks 2-3 delivered** - SQLite
> data layer, materiality engine, component/account scoping, a unique
> transaction-ID (hash) engine, a Target + NSS sampling engine, and four Streamlit
> pages (Upload / Materiality / Scoping / Sampling). Further iterations follow
> [`docs/TIMELINE.md`](docs/TIMELINE.md).

---

## In one sentence

After an audit team uploads group financial data, trial balances and transaction
detail, the system automatically **computes materiality**, decides **which
components and accounts require testing**, generates **target and non-statistical
(NSS) samples**, identifies **duplicate transactions and anomaly risks**, and
records **whether each transaction has already been tested** - reducing duplicated
voucher testing and improving audit efficiency.

The core idea: **not just finding anomalous transactions, but systematising the
audit workflow.**

## Core capabilities (V1 MVP, 8 features)

1. Upload simulated group data (engagements / components / accounts / transactions)
2. Compute materiality **PM / TE / SAD** (with version revisions)
3. **Component scoping** - group entity scope decisions
4. **Account scoping** - account-level testing decisions
5. Generate **target samples + NSS samples**
6. Assign a **unique transaction ID (hash)** to every transaction
7. Record **tested / not tested**
8. **Evidence reuse** - when a transaction is re-selected, flag it as reusable /
   partially reusable / not reusable (based on assertion coverage)

> V2 adds Red-Flag Analytics (duplicate invoices/contracts/bank references,
> same-amount frequency, concentration, etc.); V3 productionises it (multi-user,
> multi-engagement, working-paper export, ML anomaly detection). See
> [`docs/FEATURE_LIST.md`](docs/FEATURE_LIST.md).

## Tech stack (V1)

`Python` · `Pandas` · `SQLite` · `Streamlit`

## Documentation

| Document | Contents |
|---|---|
| [`docs/DESIGN_DOC.md`](docs/DESIGN_DOC.md) | System design: problem, the 9 modules, algorithms & formulas, architecture |
| [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) | ERD + all table definitions |
| [`docs/FEATURE_LIST.md`](docs/FEATURE_LIST.md) | V1 / V2 / V3 feature tiers |
| [`docs/TIMELINE.md`](docs/TIMELINE.md) | 6-week iteration plan & deliverables |
| [`data/templates/`](data/templates/) | 5 input CSV templates (with simulated sample rows) |

## Project structure

```
AuditScope/
├── README.md
├── requirements.txt
├── app.py                    # Streamlit front end (Upload / Materiality / Scoping)
├── db.py                     # SQLite data layer (schema / import / read-write)
├── engines/                  # Calculation engines (pure functions, unit-testable)
│   ├── materiality.py        #   PM / TE / SAD
│   ├── component_scoping.py  #   component scope
│   ├── account_scoping.py    #   account scope
│   ├── hashing.py            #   unique transaction ID (hash)
│   └── sampling.py           #   Target + NSS sampling
├── tests/                    # 27 engine unit tests
├── docs/
│   ├── DESIGN_DOC.md
│   ├── DATA_MODEL.md
│   ├── FEATURE_LIST.md
│   └── TIMELINE.md
└── data/
    └── templates/            # 5 input CSV templates (simulated sample)
        ├── engagements.csv
        ├── materiality_inputs.csv
        ├── components.csv
        ├── accounts.csv
        └── transactions.csv
```

## Getting started

```bash
pip install -r requirements.txt
streamlit run app.py
# On page 1, tick "Use the built-in sample template", click Import,
# then walk through Materiality -> Scoping.
```

Run the tests:

```bash
python -m pytest -q
```

The calculation engines use **only pandas / the standard library**; Streamlit and
pytest are only needed for the UI and tests respectively.

---

## Disclaimer

> This project is a personal educational prototype based on general audit concepts
> and simulated data. It does not use confidential client data or proprietary firm
> methodology. All thresholds, rules and examples are for technical demonstration
> only and do not constitute an audit opinion or methodology guidance.
