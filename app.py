"""
app.py — AuditScope Streamlit 前端(V1 · Week 2 前 3 页)
=========================================================
页面:① 上传数据 ② 重要性 ③ 范围判断
数据持久化在本地 SQLite(auditscope.db),各页通过读库共享状态。
运行:  streamlit run app.py
"""
from __future__ import annotations

import os
import sqlite3

import pandas as pd
import streamlit as st

import db
from engines import compute_materiality, score_components, score_accounts

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "auditscope.db")
TPL = os.path.join(HERE, "data", "templates")

st.set_page_config(page_title="AuditScope", page_icon="🧭", layout="wide")
db.init_db(DB_PATH)


def con():
    return db.connect(DB_PATH)


def first_engagement_id(c) -> int | None:
    row = c.execute("SELECT engagement_id FROM engagements ORDER BY engagement_id LIMIT 1").fetchone()
    return row[0] if row else None


# ============================================================ 侧边栏
st.sidebar.title("🧭 AuditScope")
st.sidebar.caption("Group Audit Sampling & Analytics — V1")
page = st.sidebar.radio("导航", ["① 上传数据", "② 重要性", "③ 范围判断"])
st.sidebar.divider()
st.sidebar.caption("教育性原型 · 模拟数据 · 不含任何客户机密或机构方法论")


# ============================================================ 页 1:上传
if page == "① 上传数据":
    st.title("① 上传集团数据")
    st.write("上传 4 类 CSV(可先用内置模板体验)。导入会写入本地 SQLite。")

    c1, c2 = st.columns(2)
    with c1:
        f_eng = st.file_uploader("engagements.csv", type="csv", key="eng")
        f_comp = st.file_uploader("components.csv", type="csv", key="comp")
    with c2:
        f_acc = st.file_uploader("accounts.csv", type="csv", key="acc")
        f_mat = st.file_uploader("materiality_inputs.csv(可选)", type="csv", key="mat")

    use_tpl = st.checkbox("改用内置示例模板(ABC Holdings FY2026)", value=False)

    if st.button("🚀 导入 / 重新导入", type="primary", use_container_width=True):
        def rd(uploaded, name):
            if use_tpl:
                return pd.read_csv(os.path.join(TPL, name))
            return pd.read_csv(uploaded) if uploaded else None

        eng = rd(f_eng, "engagements.csv")
        comp = rd(f_comp, "components.csv")
        acc = rd(f_acc, "accounts.csv")
        mat = rd(f_mat, "materiality_inputs.csv")

        if eng is None or comp is None or acc is None:
            st.error("至少需要 engagements / components / accounts 三个文件(或勾选示例模板)。")
        else:
            # 清空重建
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            db.init_db(DB_PATH)
            c = con()
            n_e = db.load_engagements(c, eng)
            n_c = db.load_components(c, comp)
            n_a = db.load_accounts(c, acc)
            c.commit()
            eid = first_engagement_id(c)
            n_m = 0
            if mat is not None and eid is not None:
                for _, r in mat.iterrows():
                    m = compute_materiality(r.to_dict())
                    db.save_materiality_version(c, eid, m, make_active=True)  # 最后一条生效
                    n_m += 1
            c.close()
            st.success(f"导入成功:engagements {n_e} · components {n_c} · "
                       f"accounts {n_a} · materiality 版本 {n_m}")
            st.info("接着去『② 重要性』确认 PM/TE/SAD,再到『③ 范围判断』。")

    st.divider()
    c = con()
    for t, label in [("engagements", "项目"), ("components", "主体"), ("accounts", "科目")]:
        df = db.read_table(c, t)
        if len(df):
            st.markdown(f"**已入库 · {label}({len(df)})**")
            st.dataframe(df, use_container_width=True, hide_index=True)
    c.close()


# ============================================================ 页 2:重要性
elif page == "② 重要性":
    st.title("② 重要性计算(PM / TE / SAD)")
    c = con()
    eid = first_engagement_id(c)
    if eid is None:
        st.warning("请先在『① 上传数据』导入项目。")
        st.stop()

    st.subheader("新增 / 修订一个版本")
    with st.form("mat"):
        cc = st.columns(3)
        btype = cc[0].selectbox("Benchmark", ["PBT", "Revenue", "Assets", "Equity"])
        amount = cc[1].number_input("Benchmark 金额", value=4000000.0, step=100000.0)
        pct = cc[2].number_input("百分比 %", value=5.0, step=0.5) / 100
        cc2 = st.columns(3)
        adj = cc2[0].number_input("调整系数", value=1.0, step=0.05)
        te_pct = cc2[1].number_input("TE %(占 PM)", value=65.0, step=5.0) / 100
        sad_pct = cc2[2].number_input("SAD %(占 PM)", value=5.0, step=1.0) / 100
        reason = st.text_input("修订原因", "V1 Initial planning")
        ok = st.form_submit_button("计算并保存为生效版本", type="primary")
    if ok:
        try:
            m = compute_materiality({
                "benchmark_type": btype, "benchmark_amount": amount, "percentage": pct,
                "adjustment_factor": adj, "te_percentage": te_pct,
                "sad_percentage": sad_pct, "reason_for_revision": reason})
            db.save_materiality_version(c, eid, m, make_active=True)
            st.success("已保存并设为当前生效版本。")
        except ValueError as e:
            st.error(f"输入有误:{e}")

    act = db.active_materiality(c, eid)
    if act:
        st.subheader("当前生效重要性")
        m1, m2, m3 = st.columns(3)
        m1.metric("PM", f"{act['pm']:,.0f}")
        m2.metric("TE(performance)", f"{act['te']:,.0f}")
        m3.metric("SAD(clearly trivial)", f"{act['sad']:,.0f}")
        st.caption(f"基准 {act['benchmark_type']} × {act['percentage']:.1%} × "
                   f"调整 {act['adjustment_factor']} · 版本原因:{act['reason_for_revision']}")

    hist = db.read_table(c, "materiality_versions")
    if len(hist):
        st.subheader("版本历史(is_active=1 为生效)")
        st.dataframe(hist[["version_id", "benchmark_type", "benchmark_amount",
                           "pm", "te", "sad", "reason_for_revision", "is_active"]],
                     use_container_width=True, hide_index=True)
    c.close()


# ============================================================ 页 3:范围判断
elif page == "③ 范围判断":
    st.title("③ 范围判断(Component & Account Scoping)")
    c = con()
    eid = first_engagement_id(c)
    if eid is None:
        st.warning("请先在『① 上传数据』导入项目。")
        st.stop()
    act = db.active_materiality(c, eid)
    if not act:
        st.warning("请先在『② 重要性』计算并保存一个生效版本。")
        st.stop()

    te, sad = act["te"], act["sad"]
    st.caption(f"使用生效重要性:TE {te:,.0f} · SAD {sad:,.0f}")

    if st.button("▶ 运行范围引擎", type="primary"):
        comp = db.read_table(c, "components").to_dict("records")
        scored_c = score_components(comp)
        for r in scored_c:
            db.update_component_scope(c, r["entity_id"], r["contribution_pct"],
                                      r["scope_decision"], r["scope_reason"])
        acc = db.read_table(c, "accounts").to_dict("records")
        scored_a = score_accounts(acc, te, sad)
        for r in scored_a:
            db.update_account_scope(c, r["account_id"], r["testing_required"],
                                    r["testing_type"], r["testing_reason"])
        st.success("范围判断完成,已写回数据库。")

    comp = db.read_table(c, "components")
    if len(comp) and comp["scope_decision"].notna().any():
        st.subheader("主体范围")
        n_full = (comp["scope_decision"] == "Full Scope").sum()
        st.caption(f"Full Scope 主体:{n_full} / {len(comp)}")
        st.dataframe(comp[["entity_name", "revenue", "pbt", "risk_rating",
                           "contribution_pct", "scope_decision", "scope_reason"]],
                     use_container_width=True, hide_index=True)

    acc = db.read_table(c, "accounts")
    if len(acc) and acc["testing_type"].notna().any():
        st.subheader("科目范围")
        n_test = (acc["testing_required"] == 1).sum()
        st.caption(f"需测试科目:{n_test} / {len(acc)}")
        st.dataframe(acc[["entity_id", "account_name", "account_type", "balance",
                          "risk_rating", "testing_required", "testing_type",
                          "testing_reason"]],
                     use_container_width=True, hide_index=True)
    c.close()
