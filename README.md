# AuditScope

**Group Audit Sampling, Evidence Reuse & Red-Flag Analytics System**
集团审计计划、抽样、证据复用与异常预警平台

> **进度:** Week 1 Design Doc 包已完成;**Week 2 已落地**——SQLite 数据层 + 重要性引擎 + component/account 范围引擎 + Streamlit 前 3 页(上传 / 重要性 / 范围)。后续按 [`docs/TIMELINE.md`](docs/TIMELINE.md) 迭代。

---

## 一句话

审计团队上传集团财务数据、试算平衡表和交易明细后,系统自动**计算重要性水平**、判断**哪些主体和科目需要测试**、生成 **target / NSS 样本**、识别**重复交易与异常风险**,并记录**每笔交易是否已被测试**,从而减少重复抽凭、提升审计效率。

项目的灵魂:**不是单纯发现异常交易,而是把审计工作流系统化。**

## 核心能力(V1 MVP · 8 项)

1. 上传模拟集团数据(engagement / components / accounts / transactions)
2. 计算重要性 **PM / TE / SAD**(支持多版本 revision)
3. **Component Scoping** 集团主体范围判断
4. **Account Scoping** 科目范围判断
5. 生成 **Target 样本 + NSS 样本**
6. 为每笔交易生成**唯一交易 ID(hash)**
7. 记录 **tested / not tested**
8. **证据复用**:同一交易再次被抽到时提示 可复用 / 部分复用 / 不可复用(基于 assertion 覆盖)

> V2 增加 Red-Flag Analytics(重复发票/合同/银行流水、同额高频、集中度等),V3 产品化(多用户、多 engagement、导出底稿、ML 异常检测)。详见 [`docs/FEATURE_LIST.md`](docs/FEATURE_LIST.md)。

## 技术栈(V1)

`Python` · `Pandas` · `SQLite` · `Streamlit` · `Plotly`

## 文档导航

| 文档 | 内容 |
|---|---|
| [`docs/DESIGN_DOC.md`](docs/DESIGN_DOC.md) | 系统设计:问题背景、9 大模块、算法与公式、架构 |
| [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) | ERD 关系图 + 全部数据表定义 |
| [`docs/FEATURE_LIST.md`](docs/FEATURE_LIST.md) | V1 / V2 / V3 功能分级 |
| [`docs/TIMELINE.md`](docs/TIMELINE.md) | 6 周迭代计划与交付物 |
| [`data/templates/`](data/templates/) | 5 个输入 CSV 模板(含模拟示例行) |

## 目录结构

```
AuditScope/
├── README.md
├── requirements.txt
├── app.py                    # Streamlit 前端(上传/重要性/范围)
├── db.py                     # SQLite 数据层(建表/导入/读写)
├── engines/                  # 计算引擎(纯函数,可单测)
│   ├── materiality.py        #   PM / TE / SAD
│   ├── component_scoping.py  #   主体范围
│   └── account_scoping.py    #   科目范围
├── tests/                    # 15 个引擎单元测试
├── docs/
│   ├── DESIGN_DOC.md
│   ├── DATA_MODEL.md
│   ├── FEATURE_LIST.md
│   └── TIMELINE.md
└── data/
    └── templates/            # 5 个输入 CSV 模板(含模拟示例)
        ├── engagements.csv
        ├── materiality_inputs.csv
        ├── components.csv
        ├── accounts.csv
        └── transactions.csv
```

## 快速开始(V1 落地后)

```bash
pip install -r requirements.txt
streamlit run app.py
# 依次上传 data/templates/ 下的 5 个 CSV,即可跑通 重要性 → 范围 → 抽样 → 证据复用
```

---

## 免责声明 / Disclaimer

> This project is a personal educational prototype based on general audit concepts and simulated data. It does not use confidential client data or proprietary firm methodology.
>
> 本项目为个人学习原型,基于通用审计概念与**完全模拟的数据**构建,**不包含任何客户机密数据或任何审计机构的内部专有方法论**。所有阈值、规则与示例仅用于技术演示,不构成审计意见或方法论建议。
