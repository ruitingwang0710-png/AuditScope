# AuditScope - 6-Week Iteration Timeline

Cadence: design clearly first, then ship a demoable result each week.

---

## Week 1 - Design Doc + Data Model (done)
No rush to write complex code this week; get the system design clear first.

Deliverables:
- [x] Design document (`docs/DESIGN_DOC.md`)
- [x] ERD data model (`docs/DATA_MODEL.md`)
- [x] Sample CSV templates (`data/templates/`)
- [x] GitHub repo structure
- [x] README skeleton (with disclaimer)

## Week 2 - Materiality + Scoping (done)
Deliverables:
- [x] Materiality calculator (PM/TE/SAD + versioning) - `engines/materiality.py`
- [x] Component scoping engine - `engines/component_scoping.py`
- [x] Account scoping engine - `engines/account_scoping.py`
- [x] Streamlit first 3 pages (Upload / Materiality / Scoping) - `app.py`
- [x] SQLite schema script - `db.py`
- [x] 15 engine unit tests (`tests/`), end-to-end verified

## Week 3 - Sampling + Unique ID (done)
Deliverables:
- [x] Transaction hash generator (exact match) - `engines/hashing.py`
- [x] Target sampling (>= TE / round amount / month-year-end) - `engines/sampling.py`
- [x] NSS sampling (fixed-size, from remainder, seeded) - `engines/sampling.py`
- [x] Sample result table + Streamlit sampling page (page 4) - `app.py`
- [x] 12 more unit tests (hashing + sampling); end-to-end verified

## Week 4 - Evidence Reuse
Deliverables:
- [ ] Evidence test recording
- [ ] Assertion coverage assessment
- [ ] Reusable / partial / not reusable logic
- [ ] Evidence reuse dashboard

## Week 5 - Red-Flag Alerts (enter V2)
Deliverables:
- [ ] Duplicate invoice / contract / bank reference alerts
- [ ] Same-amount high-frequency alert
- [ ] Missing evidence (missing contract number / missing bank receipt) alerts
- [ ] Counterparty concentration alert
- [ ] Red-flag -> target sample linkage

## Week 6 - Polish + GitHub + Resume
Deliverables:
- [ ] README (complete)
- [ ] Screenshots
- [ ] Demo video / GIF
- [ ] Clean repo
- [ ] Resume bullet + interview talking points

---

## Milestones

| Milestone | Timing | Publicly demoable result |
|---|---|---|
| M0 Design finalised | End of Week 1 | Full design-doc package |
| M1 Planning automated | End of Week 2 | Upload data -> auto materiality & scope |
| M2 Sampling usable | End of Week 3 | One-click target + NSS sample list |
| M3 Evidence reuse (the soul) | End of Week 4 | Detect tested transactions across accounts + reuse advice |
| M4 Analytics complete | End of Week 5 | Red-flag alerts + linked sampling |
| M5 Portfolio-ready | End of Week 6 | Ready for GitHub / CV / interview |
```
