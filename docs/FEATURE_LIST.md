# AuditScope — 功能清单(V1 / V2 / V3)

分三个版本迭代,做成产品迭代而非一次性大系统。

---

## Version 1 — MVP(2–3 周)
目标:跑通核心逻辑,能放 GitHub,能写进简历。

| # | 功能 | 模块 | 状态 |
|---|---|---|---|
| 1 | 上传模拟集团数据(4 类 CSV) | M1 | ☐ |
| 2 | 计算 PM / TE / SAD(多版本) | M2 | ☐ |
| 3 | Component scope 判断(带理由) | M3 | ☐ |
| 4 | Account scope 判断(带理由) | M4 | ☐ |
| 5 | 生成 Target 样本 + NSS 样本 | M5 | ☐ |
| 6 | 每笔交易唯一 ID(exact-match hash) | M6 | ☐ |
| 7 | 记录 tested / not tested | M7 | ☐ |
| 8 | 证据复用:可复用 / 部分 / 不可(assertion 覆盖) | M7 | ☐ |
| 9 | 简版 Dashboard(关键指标) | M9 | ☐ |

技术栈:`Python · Pandas · SQLite · Streamlit · GitHub`

---

## Version 2 — Red-Flag Analytics(4–6 周)
目标:更像 audit analytics / data assurance。

| # | 功能 | 模块 |
|---|---|---|
| 1 | 重复合同号报警 | M8 |
| 2 | 重复银行流水号报警 | M8 |
| 3 | 重复发票号报警 | M8 |
| 4 | 同 counterparty 同额高频报警 | M8 |
| 5 | 高金额缺合同号报警 | M8 |
| 6 | 收入缺银行流水匹配报警 | M8 |
| 7 | 月末 / 年末集中确认收入报警 | M8 |
| 8 | 银行 / 客户 / 供应商集中度分析 | M8 |
| 9 | Red-flag → 高分交易自动进 target | M5×M8 |

新增表:`alerts`、`reference_links`、`counterparty_exposure`

一句话卖点:*"I designed a red-flag alert engine based on audit trail references and transaction patterns."*

---

## Version 3 — Full Product(长期作品集)
目标:像一个真的产品。

| # | 功能 |
|---|---|
| 1 | 用户登录 |
| 2 | 多 engagement 管理 |
| 3 | 多版本 materiality revision(完整 UI) |
| 4 | 抽样历史记录 |
| 5 | 审计 adjustment 后自动重算 scope |
| 6 | AI 生成 audit memo |
| 7 | 导出 Excel working paper |
| 8 | Dashboard summary(完整) |
| 9 | ML anomaly detection |
| 10 | Role-based access control |
| 11 | Fuzzy transaction match |

技术栈升级:`React/Next.js · FastAPI · PostgreSQL · Pandas · scikit-learn · Plotly/Power BI · Docker · Render/Railway/AWS`

> 建议:先把 V1 Streamlit 做扎实,再逐步升级,不要一开始上产品化架构。

---

## 简历写法(达到 V1 + 部分 V2 后)

```
AuditScope — Group Audit Sampling & Red-Flag Analytics System
Python · SQL · Streamlit · SQLite · Pandas · Audit Analytics

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
