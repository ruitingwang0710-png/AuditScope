# AuditScope — 系统设计文档

**版本:** Design Doc v1.0 (Week 1)
**范围:** 覆盖完整系统愿景;明确标注 V1 MVP 实现边界。
**状态:** 设计定稿,待进入 V1 编码。

---

## 1. 问题背景

集团审计(group audit)在计划与执行阶段有几个反复出现的痛点:

1. **重要性反复修订。** 审计调整(audit adjustments)发生后,PM 会被重算,进而牵动 component / account scope 与样本量,手工维护极易出错且无版本追溯。
2. **范围判断靠经验。** 哪些子公司要做 full scope、哪些科目要详细测试,常散落在 Excel 与个人判断里,缺乏一致、可复核的规则。
3. **重复抽凭。** 同一笔交易在不同科目、不同 assertion 下被反复抽样测试,浪费工时——却没有系统识别"这笔其实测过了"。
4. **异常识别滞后。** 重复发票号、重复银行流水、同额高频交易、集中度风险等,往往在复核晚期才被发现。

**AuditScope 的定位:把上述工作流系统化、规则化、可复核化**,而不仅仅是"找异常交易"。

## 2. 系统愿景

```
上传集团数据(TB + 交易明细)
        │
        ▼
  重要性计算(PM/TE/SAD,多版本)
        │
        ▼
  主体范围判断(Component Scoping)
        │
        ▼
  科目范围判断(Account Scoping)
        │
        ▼
  抽样引擎(Target + NSS)
        │
        ├─ 唯一交易 ID(hash)贯穿全流程
        │
        ▼
  证据复用(assertion 覆盖判断)
        │
        ▼
  异常预警(Red-Flag,V2)
        │
        ▼
  复核看板(Dashboard)
```

系统由 **6 个核心引擎 + 1 个 dashboard 层**组成(见第 4 节模块设计)。

## 3. 用户与用例

| 角色 | 关注点 | 典型操作 |
|---|---|---|
| 审计计划负责人 | 重要性与范围的一致性、可追溯 | 设定 benchmark、复核 scope 决策 |
| 现场审计员 | 抽样清单、避免重复抽凭 | 生成样本、登记测试结果 |
| 复核 / 经理 | 整体进度、风险热点、节省工时 | 看 dashboard、审阅 red-flag |
| 数据 assurance | 异常模式、参照链完整性 | 配置 red-flag 规则(V2) |

核心用例:*"上传 ABC 集团 FY2026 试算表与交易明细 → 系统算出 PM/TE/SAD → 标出 3 家 full scope 主体和需测科目 → 生成 target+NSS 样本 → 现场登记测试 → 当 AR 再次抽到某笔已在 Revenue 测过的交易时,系统提示可部分复用,只需补做 valuation 程序。"*

## 4. 模块设计(9 模块)

> 图例:**[V1]** = MVP 实现;**[V2]** = Red-Flag 阶段;**[V3]** = 产品化阶段。

### Module 1 — Engagement Setup **[V1]**
项目入口。创建审计项目并隔离数据,使系统支持**多个集团项目**而非单个 CSV。
字段:engagement name、group name、financial year、currency、industry、risk level、prepared by、reviewed by。

### Module 2 — Materiality Calculator **[V1]**
输入 benchmark type(PBT / Revenue / Assets / Equity)、benchmark amount、percentage、adjustment factor、PM%(→TE)、SAD%。

计算公式:

```
PM  (Planning Materiality)     = Benchmark × Percentage × Adjustment Factor
TE  (Performance Materiality)  = PM × TE_Percentage        # 通常 50%–75%
SAD (Clearly Trivial / 明显微小) = PM × SAD_Percentage       # 通常 5%
Target testing threshold       = TE                         # 单笔 ≥ TE 进 target(见 M5)
```

**多版本(materiality revision)是关键:** 每次重算都落 `materiality_versions` 一行,记录 `reason_for_revision`(如 V1 Initial planning / V2 After audit adjustment / V3 Final)。scope 与样本以"当前生效版本"为准,历史可回溯。

### Module 3 — Component Scoping Engine **[V1]**
输入每个 entity 的 revenue / pbt / assets / liabilities / risk_rating / prior_year_adjustment。
先计算贡献度:`contribution% = entity_metric / group_total_metric`(revenue 与 pbt 各算一套,取更保守者)。

判定规则(阈值可配置,默认):

```
if revenue_contribution > 15%  or  pbt_contribution > 15%:   Full Scope
elif risk_rating == High:                                    Specific Scope
elif 5% <= contribution <= 15%:                              Specific Scope
else:                                                        Analytical Review
```

输出:Entity / Contribution% / Scope / Reason(每条决策都带可读理由)。

### Module 4 — Account Scoping Engine **[V1]**
对每个 in-scope 主体的 TB 逐科目判断。
输入:account_code / account_name / account_type / balance / movement / risk_rating。

判定逻辑:

```
if risk_rating == High:                         Testing required · type = Target(+NSS 若为交易性科目)
elif balance > TE  or  movement > TE:           Testing required · type = Target + NSS
elif balance <= SAD:                            No detailed testing
else:                                           NSS only(或 Analytical)
```

输出示例:

```
Entity A | Revenue | 8,000,000 | Testing required | Target + NSS | Exceeds TE
Entity A | AR      | 2,000,000 | Testing required | NSS          | Exceeds TE
Entity B | Tax     |    80,000 | Testing required | Specific     | High risk (低余额高风险)
Entity A | Office  |    12,000 | No testing        | —            | Below SAD
```

体现:**不是所有科目都测**,而是由 materiality × risk × account type 共同决定。

### Module 5 — Sampling Engine **[V1]**
对"需测试"科目读取 transaction population,分两步:

**A. Target testing(定向挑选)** — 自动选:金额 ≥ TE 的大额、超阈值项、red-flag 项(V2)、关联方交易、手工调整、月末/年末交易。

**B. NSS testing(非统计抽样)** — 从剩余总体抽固定数量:
```
population_remaining = all_txn − target_selected − reusable_already_tested
NSS sample = 从 population_remaining 中按固定样本量抽取(可分层)
```

输出字段:sample_id / entity_id / account_code / transaction_hash / sample_type / selection_reason / testing_status / reuse_status。
**联动:** red-flag_score 高的交易即使金额不大也会被拉入 target(V2)。

### Module 6 — Unique Transaction ID Engine **[V1] 技术核心**
解决"同一笔交易在不同账套/科目/测试中如何识别为同一笔"。生成稳定 hash:

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
# → TXN-8F3A91C2B7D4E102
```

分两层匹配:
- **Exact match(V1):** 上述关键字段完全一致。
- **Fuzzy match(V3):** 同一供应商 + 相近日期 + 相同金额 + 相似发票号(编辑距离),用于现实脏数据。

### Module 7 — Evidence Reuse Tracker **[V1] 最独特点**
每次测试落 `evidence_tests`:transaction_hash / tested_account / tested_assertions / evidence_type / evidence_reference / test_result / prepared_by / reviewed_by / test_date。

当同一 hash 被另一科目抽到时,做 **assertion 覆盖判断**:

```
已测覆盖 assertions  ∩  本次科目所需 assertions
= 完全覆盖 → Reusable
= 部分覆盖 → Partially reusable(列出仍需补做的 assertion)
= 无交集   → Not reusable
```

示例:
```
Revenue 已测:Occurrence, Accuracy, Cut-off
AR 需要   :Existence, Valuation, Accuracy
判断      :Accuracy 可复用;Existence/Valuation 未覆盖
结论      :Partially reusable → 仅需补做 Existence + Valuation 程序
```

关键:**不是"测过就不用测",而是引入 assertion coverage 做细粒度复用**——这是项目最专业的差异化点。

### Module 8 — Red-Flag Alert Engine **[V2]**
规则型异常检测,每条 alert 带 alert_type / severity / alert_score / description / recommended_action:
重复合同号、重复银行流水号、重复发票号、同 counterparty 同额高频、高额缺合同号、收入缺收款流水匹配、月末/年末集中确认、银行/客户/供应商集中度。
与 M5 联动:`red_flag_score 高 → 进 target sample`。

### Module 9 — Dashboard & Review Center **[V1 简版 / V3 完整]**
页面:Engagement Overview / Materiality & Scope / Component Scope / Account Scope / Sample Selection / Evidence Reuse / Red-Flag Alerts / Review Summary。
关键指标:in-scope 主体数、需测科目数、target/NSS 样本数、**避免的重复样本数**、可复用证据数、高风险 alert 数、**Estimated time saved**。

> **Estimated time saved 是把技术成果转成 business impact 的点:**
> `避免重复样本 42 笔 × 每笔 15 分钟 = 节省 10.5 小时`。

## 5. 架构(V1)

```
┌────────────────────────────────────────────┐
│                Streamlit UI                  │  多页:上传 / 重要性 / 范围 / 抽样 / 复用 / 看板
├────────────────────────────────────────────┤
│            服务层 (Python 纯函数)             │
│  materiality · scoping · sampling · hashing  │
│  evidence_reuse · (redflag V2)               │
├────────────────────────────────────────────┤
│      数据访问层 (repository, sqlite3)         │
├────────────────────────────────────────────┤
│                 SQLite DB                     │  见 DATA_MODEL.md
└────────────────────────────────────────────┘
       Pandas 负责 CSV 载入 / 清洗 / 向量化计算
```

设计原则:**引擎与 UI 分离**(引擎为可单测的纯函数)、**规则可配置**(阈值集中在配置,不散落于代码)、**每个决策可解释**(scope/sample/reuse 都产出 reason 字段)。

## 6. V1 MVP 实现边界

**做:** Module 1–7 + Module 9 简版看板;exact-match hash;SQLite 持久化;Streamlit 多页;模拟数据模板。
**不做(留待 V2/V3):** Red-Flag 引擎(M8)、fuzzy match、用户登录/RBAC、AI audit memo、React/FastAPI、Docker 部署、ML 异常检测。

验收标准:上传 5 个 CSV → 得到带 reason 的 scope 决策 → 生成 target+NSS 样本 → 登记一笔测试 → 该交易在另一科目被抽到时正确显示 Reusable / Partial / Not。

## 7. 风险与边界

- **数据真实性:** 全部使用模拟数据;阈值为演示默认值,需按机构政策校准。
- **方法论合规:** 见 README 免责声明——不含任何机构内部方法论或客户机密。
- **可扩展性:** V1 用 SQLite/Streamlit 快速验证;数据量或多用户需求上来后按 V3 迁移 PostgreSQL/FastAPI。
