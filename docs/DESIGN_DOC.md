# AuditScope - System Design Document

**Version:** Design Doc v1.0 (Week 1)
**Scope:** Covers the full system vision; the V1 MVP implementation boundary is
clearly marked.
**Status:** Design finalised; V1 coding in progress.

---

## 1. Problem background

Group audits face several recurring pain points during planning and execution:

1. **Materiality is revised repeatedly.** After audit adjustments, PM is
   recalculated, which cascades into component/account scope and sample sizes.
   Maintaining this by hand is error-prone and lacks version traceability.
2. **Scoping relies on judgement.** Which subsidiaries need full scope and which
   accounts need detailed testing often lives in scattered spreadsheets and
   individual judgement, without a consistent, reviewable rule set.
3. **Duplicated voucher testing.** The same transaction gets sampled and tested
   repeatedly across different accounts and assertions, wasting effort - with no
   system recognising that "this one has already been tested".
4. **Late anomaly detection.** Duplicate invoice numbers, duplicate bank
   references, same-amount high-frequency transactions and concentration risk are
   often surfaced only late in review.

**AuditScope's positioning: systematise, ruleify and make reviewable the workflow
above** - not merely "find anomalous transactions".

## 2. System vision

```
Upload group data (TB + transaction detail)
        |
        v
  Materiality (PM/TE/SAD, versioned)
        |
        v
  Component scoping
        |
        v
  Account scoping
        |
        v
  Sampling engine (Target + NSS)
        |
        +-- unique transaction ID (hash) threads through the whole flow
        |
        v
  Evidence reuse (assertion coverage)
        |
        v
  Red-flag alerts (V2)
        |
        v
  Review dashboard
```

The system is made up of **6 core engines + 1 dashboard layer** (see Section 4).

## 3. Users and use case

| Role | Focus | Typical actions |
|---|---|---|
| Audit planning lead | Consistent, traceable materiality & scope | Set benchmark, review scope decisions |
| Field auditor | Sample lists, avoid duplicated testing | Generate samples, record test results |
| Reviewer / manager | Overall progress, risk hotspots, time saved | Review dashboard, review red flags |
| Data assurance | Anomaly patterns, reference-link integrity | Configure red-flag rules (V2) |

Core use case: *"Upload ABC Group's FY2026 trial balance and transaction detail ->
the system computes PM/TE/SAD -> it marks 3 full-scope components and the accounts
requiring testing -> it generates target + NSS samples -> the field team records
tests -> when AR later selects a transaction already tested under Revenue, the
system flags it as partially reusable, requiring only additional valuation
procedures."*

## 4. Module design (9 modules)

> Legend: **[V1]** = MVP; **[V2]** = Red-Flag phase; **[V3]** = productionisation.

### Module 1 - Engagement Setup **[V1]**
The entry point. Creates an audit engagement and isolates its data, so the system
supports **multiple group engagements** rather than a single CSV.
Fields: engagement name, group name, financial year, currency, industry, risk
level, prepared by, reviewed by.

### Module 2 - Materiality Calculator **[V1]**
Inputs: benchmark type (PBT / Revenue / Assets / Equity), benchmark amount,
percentage, adjustment factor, PM% (-> TE), SAD%.

Formulas:

```
PM  (Planning Materiality)     = Benchmark x Percentage x Adjustment Factor
TE  (Performance Materiality)  = PM x TE_Percentage        # typically 50%-75%
SAD (Clearly Trivial)          = PM x SAD_Percentage       # typically 5%
Target testing threshold       = TE                         # items >= TE go to target (see M5)
```

**Versioning (materiality revision) is key:** each recalculation writes a row to
`materiality_versions` recording `reason_for_revision` (e.g. V1 Initial planning /
V2 After audit adjustment / V3 Final). Scope and samples use the "currently active
version", with full history retained.

### Module 3 - Component Scoping Engine **[V1]**
Inputs per entity: revenue / pbt / assets / liabilities / risk_rating /
prior_year_adjustment. First computes contribution:
`contribution% = entity_metric / group_total_metric` (computed for both revenue and
pbt, taking the more conservative = higher value).

Decision rules (thresholds configurable, defaults shown):

```
if revenue_contribution > 15%  or  pbt_contribution > 15%:   Full Scope
elif risk_rating == High:                                    Specific Scope
elif 5% <= contribution <= 15%:                              Specific Scope
else:                                                        Analytical Review
```

Output: Entity / Contribution% / Scope / Reason (every decision carries a readable
rationale).

### Module 4 - Account Scoping Engine **[V1]**
Assesses each in-scope entity's TB account by account.
Inputs: account_code / account_name / account_type / balance / movement /
risk_rating.

Decision logic:

```
if risk_rating == High:                         Testing required, type = Target (+ NSS if transactional)
elif balance > TE  or  movement > TE:           Testing required, type = Target + NSS
elif balance <= SAD:                            No detailed testing
else:                                           NSS only (or Analytical)
```

Example output:

```
Entity A | Revenue | 8,000,000 | Testing required | Target + NSS | Exceeds TE
Entity A | AR      | 2,000,000 | Testing required | NSS          | Exceeds TE
Entity B | Tax     |    80,000 | Testing required | Specific     | High risk (low balance, high risk)
Entity A | Office  |    12,000 | No testing        | -            | Below SAD
```

The point: **not every account is tested** - it is determined jointly by
materiality x risk x account type.

### Module 5 - Sampling Engine **[V1]**
For accounts flagged as "testing required", read the transaction population and
run two steps:

**A. Target testing (directed selection)** - automatically pick: large items
>= TE, over-threshold items, red-flag items (V2), related-party transactions,
manual adjustments, month-end/year-end transactions.

**B. NSS testing (non-statistical sampling)** - sample a fixed count from the
remainder:
```
population_remaining = all_txn - target_selected - reusable_already_tested
NSS sample = select a fixed sample size from population_remaining (stratifiable)
```

Output fields: sample_id / entity_id / account_code / transaction_hash /
sample_type / selection_reason / testing_status / reuse_status.
**Linkage:** transactions with a high red-flag score are pulled into target even if
the amount is small (V2).

### Module 6 - Unique Transaction ID Engine **[V1] technical core**
Solves "how to recognise that a transaction appearing across different ledgers /
accounts / tests is in fact the same one". Generates a stable hash:

```python
import hashlib

def generate_transaction_hash(row):
    key = "|".join([
        str(row["entity_id"]),
        str(row["invoice_number"]),
        str(row["contract_number"]),
        str(row["bank_reference_number"]),
        str(row["counterparty_id"]),
        str(row["transaction_date"]),
        str(row["amount"]),
        str(row["currency"]),
    ])
    return "TXN-" + hashlib.sha256(key.encode()).hexdigest()[:16].upper()
# -> TXN-8F3A91C2B7D4E102
```

Two matching layers:
- **Exact match (V1):** the key fields above match exactly.
- **Fuzzy match (V3):** same supplier + close date + same amount + similar invoice
  number (edit distance), for real-world messy data.

### Module 7 - Evidence Reuse Tracker **[V1] most distinctive feature**
Each test writes to `evidence_tests`: transaction_hash / tested_account /
tested_assertions / evidence_type / evidence_reference / test_result /
prepared_by / reviewed_by / test_date.

When the same hash is selected under another account, it performs an **assertion
coverage** check:

```
assertions already tested  ∩  assertions required by this account
= fully covered   -> Reusable
= partially       -> Partially reusable (lists the assertions still to perform)
= no overlap      -> Not reusable
```

Example:
```
Revenue already tested: Occurrence, Accuracy, Cut-off
AR requires:            Existence, Valuation, Accuracy
Assessment:             Accuracy reusable; Existence/Valuation not covered
Conclusion:             Partially reusable -> only perform Existence + Valuation
```

Key point: **not "if tested then skip", but fine-grained reuse via assertion
coverage** - the most professional differentiator of the project.

### Module 8 - Red-Flag Alert Engine **[V2]**
Rule-based anomaly detection; each alert carries alert_type / severity /
alert_score / description / recommended_action: duplicate contract number,
duplicate bank reference, duplicate invoice number, same counterparty + same amount
high frequency, high amount missing contract number, revenue without matching bank
receipt, month-end/year-end revenue concentration, bank/customer/supplier
concentration. Linked to M5: `high red_flag_score -> pulled into target sample`.

### Module 9 - Dashboard & Review Center **[V1 lite / V3 full]**
Pages: Engagement Overview / Materiality & Scope / Component Scope / Account Scope
/ Sample Selection / Evidence Reuse / Red-Flag Alerts / Review Summary.
Key metrics: in-scope components, accounts requiring testing, target/NSS sample
counts, **duplicate samples avoided**, reusable evidence count, high-risk alert
count, **Estimated time saved**.

> **Estimated time saved turns technical results into business impact:**
> `42 duplicate samples avoided x 15 minutes each = 10.5 hours saved`.

## 5. Architecture (V1)

```
+----------------------------------------------+
|                Streamlit UI                  |  pages: Upload / Materiality / Scope / Sampling / Reuse / Dashboard
+----------------------------------------------+
|            Service layer (pure Python)       |
|  materiality . scoping . sampling . hashing  |
|  evidence_reuse . (redflag V2)               |
+----------------------------------------------+
|      Data access layer (repository, sqlite3) |
+----------------------------------------------+
|                 SQLite DB                     |  see DATA_MODEL.md
+----------------------------------------------+
       Pandas handles CSV load / cleaning / vectorised computation
```

Design principles: **engines separated from UI** (engines are unit-testable pure
functions); **rules are configurable** (thresholds centralised, not scattered in
code); **every decision is explainable** (scope/sample/reuse all produce a reason
field).

## 6. V1 MVP implementation boundary

**In:** Modules 1-7 + Module 9 lite dashboard; exact-match hash; SQLite
persistence; multi-page Streamlit; simulated data templates.
**Out (deferred to V2/V3):** Red-Flag engine (M8), fuzzy match, user login/RBAC,
AI audit memo, React/FastAPI, Docker deployment, ML anomaly detection.

Acceptance: upload 5 CSVs -> get scope decisions with reasons -> generate target +
NSS samples -> record a test -> when that transaction is selected under another
account, correctly show Reusable / Partial / Not.

## 7. Risks and boundaries

- **Data authenticity:** all data is simulated; thresholds are demonstration
  defaults and must be calibrated to firm policy.
- **Methodology compliance:** see README disclaimer - contains no proprietary firm
  methodology or client-confidential information.
- **Scalability:** V1 uses SQLite/Streamlit for fast validation; migrate to
  PostgreSQL/FastAPI per V3 once data volume or multi-user needs grow.
