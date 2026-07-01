# AuditScope - Feature List (V1 / V2 / V3)

Delivered as three product iterations rather than one big system.

---

## Version 1 - MVP (2-3 weeks)
Goal: get the core logic working, put it on GitHub, put it on the CV.

| # | Feature | Module | Status |
|---|---|---|---|
| 1 | Upload simulated group data (4 CSV types) | M1 | done |
| 2 | Compute PM / TE / SAD (versioned) | M2 | done |
| 3 | Component scope decision (with rationale) | M3 | done |
| 4 | Account scope decision (with rationale) | M4 | done |
| 5 | Generate target samples + NSS samples | M5 | planned (Week 3) |
| 6 | Unique transaction ID (exact-match hash) | M6 | planned (Week 3) |
| 7 | Record tested / not tested | M7 | planned (Week 4) |
| 8 | Evidence reuse: reusable / partial / not (assertion coverage) | M7 | planned (Week 4) |
| 9 | Lite dashboard (key metrics) | M9 | planned |

Tech stack: `Python . Pandas . SQLite . Streamlit . GitHub`

---

## Version 2 - Red-Flag Analytics (4-6 weeks)
Goal: make it look more like audit analytics / data assurance.

| # | Feature | Module |
|---|---|---|
| 1 | Duplicate contract number alert | M8 |
| 2 | Duplicate bank reference alert | M8 |
| 3 | Duplicate invoice number alert | M8 |
| 4 | Same counterparty + same amount high frequency alert | M8 |
| 5 | High amount missing contract number alert | M8 |
| 6 | Revenue without matching bank receipt alert | M8 |
| 7 | Month-end / year-end revenue concentration alert | M8 |
| 8 | Bank / customer / supplier concentration analysis | M8 |
| 9 | Red-flag -> high-score transaction auto-enters target | M5 x M8 |

New tables: `alerts`, `reference_links`, `counterparty_exposure`

One-line pitch: *"I designed a red-flag alert engine based on audit trail
references and transaction patterns."*

---

## Version 3 - Full Product (long-term portfolio project)
Goal: behave like a real product.

| # | Feature |
|---|---|
| 1 | User login |
| 2 | Multi-engagement management |
| 3 | Multi-version materiality revision (full UI) |
| 4 | Sampling history |
| 5 | Auto re-scope after audit adjustments |
| 6 | AI-generated audit memo |
| 7 | Export Excel working paper |
| 8 | Dashboard summary (full) |
| 9 | ML anomaly detection |
| 10 | Role-based access control |
| 11 | Fuzzy transaction match |

Upgraded stack: `React/Next.js . FastAPI . PostgreSQL . Pandas . scikit-learn .
Plotly/Power BI . Docker . Render/Railway/AWS`

> Recommendation: get the V1 Streamlit version solid first, then upgrade
> incrementally - don't jump to the production architecture up front.

---

## CV bullet (after reaching V1 + part of V2)

```
AuditScope - Group Audit Sampling & Red-Flag Analytics System
Python . SQL . Streamlit . SQLite . Pandas . Audit Analytics

- Built an audit analytics platform to calculate group materiality, determine
  component and account scoping, and generate target and non-statistical samples
  for transaction testing across multiple entities.
- Designed a unique transaction identification and evidence reuse mechanism to
  detect previously tested items across related accounts, reducing duplicated
  voucher testing and supporting assertion-level reuse decisions.
- Implemented a rule-based red-flag alert engine to identify duplicate bank
  references, repeated same-amount transactions, missing contract references and
  counterparty concentration risks, feeding high-risk items into sample selection.
```
