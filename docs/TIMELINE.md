# AuditScope — 6 周迭代时间线

节奏:先设计清楚,再按周迭代出可演示成果。

---

## Week 1 — Design Doc + 数据模型 ✅(本周)
本周不急着写复杂代码,先把系统设计清楚。

交付物:
- [x] Design document(`docs/DESIGN_DOC.md`)
- [x] ERD 数据库关系图(`docs/DATA_MODEL.md`)
- [x] Sample CSV templates(`data/templates/`)
- [x] GitHub repo 结构
- [x] README skeleton(含免责声明)

## Week 2 — Materiality + Scoping ✅
交付物:
- [x] Materiality calculator(PM/TE/SAD + 多版本)— `engines/materiality.py`
- [x] Component scoping engine — `engines/component_scoping.py`
- [x] Account scoping engine — `engines/account_scoping.py`
- [x] Streamlit 前 3 页(上传 / 重要性 / 范围)— `app.py`
- [x] SQLite schema 建表脚本 — `db.py`
- [x] 15 个引擎单元测试(`tests/`),端到端跑通

## Week 3 — Sampling + Unique ID
交付物:
- [ ] Transaction hash generator(exact match)
- [ ] Target sampling
- [ ] NSS sampling
- [ ] Sample result table + Streamlit 抽样页

## Week 4 — Evidence Reuse
交付物:
- [ ] Evidence test recording(登记测试)
- [ ] Assertion coverage 判断
- [ ] Reuse / partial / not reusable 逻辑
- [ ] Evidence reuse dashboard

## Week 5 — Red-Flag Alerts(进入 V2)
交付物:
- [ ] 重复发票 / 合同 / 银行流水报警
- [ ] 同额高频报警
- [ ] 缺证据(缺合同号 / 缺收款流水)报警
- [ ] Counterparty 集中度报警
- [ ] Red-flag → target sample 联动

## Week 6 — Polish + GitHub + Resume
交付物:
- [ ] README(完整)
- [ ] Screenshots
- [ ] Demo video / GIF
- [ ] Clean repo
- [ ] Resume bullet + 面试讲解稿

---

## 里程碑

| 里程碑 | 时点 | 可对外展示的成果 |
|---|---|---|
| M0 设计定稿 | Week 1 末 | 完整 Design Doc 包(即本次交付) |
| M1 计划自动化 | Week 2 末 | 上传数据 → 自动出重要性与范围 |
| M2 抽样可用 | Week 3 末 | 一键生成 target+NSS 样本清单 |
| M3 证据复用(灵魂功能) | Week 4 末 | 跨科目识别已测交易并给复用建议 |
| M4 analytics 完整 | Week 5 末 | Red-flag 预警 + 联动抽样 |
| M5 作品集就绪 | Week 6 末 | 可放 GitHub / 写简历 / 面试讲 |
