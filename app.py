"""
app.py - AuditScope Streamlit front end (V1, Week 2, first 3 pages)
===================================================================
Pages: (1) Upload Data  (2) Materiality  (3) Scoping
Data is persisted in a local SQLite database (auditscope.db); pages share
state by reading from the database.
Run with:  streamlit run app.py
"""
from __future__ import annotations

import os

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


# ============================================================ Sidebar
st.sidebar.title("🧭 AuditScope")
st.sidebar.caption("Group Audit Sampling & Analytics - V1")
page = st.sidebar.radio("Navigation", ["1 - Upload Data", "2 - Materiality", "3 - Scoping"])
st.sidebar.divider()
st.sidebar.caption("Educational prototype - simulated data - no client-confidential "
                   "information or proprietary firm methodology")


# ============================================================ Page 1: Upload
if page == "1 - Upload Data":
    st.title("1 - Upload Group Data")
    st.write("Upload the 4 CSV files (or try the built-in sample first). "
             "Importing writes the data into a local SQLite database.")

    c1, c2 = st.columns(2)
    with c1:
        f_eng = st.file_uploader("engagements.csv", type="csv", key="eng")
        f_comp = st.file_uploader("components.csv", type="csv", key="comp")
    with c2:
        f_acc = st.file_uploader("accounts.csv", type="csv", key="acc")
        f_mat = st.file_uploader("materiality_inputs.csv (optional)", type="csv", key="mat")

    use_tpl = st.checkbox("Use the built-in sample template (ABC Holdings FY2026)", value=False)

    if st.button("Import / Re-import", type="primary", use_container_width=True):
        def rd(uploaded, name):
            if use_tpl:
                return pd.read_csv(os.path.join(TPL, name))
            return pd.read_csv(uploaded) if uploaded else None

        eng = rd(f_eng, "engagements.csv")
        comp = rd(f_comp, "components.csv")
        acc = rd(f_acc, "accounts.csv")
        mat = rd(f_mat, "materiality_inputs.csv")

        if eng is None or comp is None or acc is None:
            st.error("engagements / components / accounts are required "
                     "(or tick the sample template).")
        else:
            # Rebuild from scratch
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
                    db.save_materiality_version(c, eid, m, make_active=True)  # last one active
                    n_m += 1
            c.close()
            st.success(f"Imported: engagements {n_e} - components {n_c} - "
                       f"accounts {n_a} - materiality versions {n_m}")
            st.info("Next, open '2 - Materiality' to confirm PM/TE/SAD, then '3 - Scoping'.")

    st.divider()
    c = con()
    for t, label in [("engagements", "Engagements"), ("components", "Components"),
                     ("accounts", "Accounts")]:
        df = db.read_table(c, t)
        if len(df):
            st.markdown(f"**Loaded - {label} ({len(df)})**")
            st.dataframe(df, use_container_width=True, hide_index=True)
    c.close()


# ============================================================ Page 2: Materiality
elif page == "2 - Materiality":
    st.title("2 - Materiality (PM / TE / SAD)")
    c = con()
    eid = first_engagement_id(c)
    if eid is None:
        st.warning("Please import an engagement on '1 - Upload Data' first.")
        st.stop()

    st.subheader("Add / revise a version")
    with st.form("mat"):
        cc = st.columns(3)
        btype = cc[0].selectbox("Benchmark", ["PBT", "Revenue", "Assets", "Equity"])
        amount = cc[1].number_input("Benchmark amount", value=4000000.0, step=100000.0)
        pct = cc[2].number_input("Percentage %", value=5.0, step=0.5) / 100
        cc2 = st.columns(3)
        adj = cc2[0].number_input("Adjustment factor", value=1.0, step=0.05)
        te_pct = cc2[1].number_input("TE % (of PM)", value=65.0, step=5.0) / 100
        sad_pct = cc2[2].number_input("SAD % (of PM)", value=5.0, step=1.0) / 100
        reason = st.text_input("Reason for revision", "V1 Initial planning")
        ok = st.form_submit_button("Compute & save as active version", type="primary")
    if ok:
        try:
            m = compute_materiality({
                "benchmark_type": btype, "benchmark_amount": amount, "percentage": pct,
                "adjustment_factor": adj, "te_percentage": te_pct,
                "sad_percentage": sad_pct, "reason_for_revision": reason})
            db.save_materiality_version(c, eid, m, make_active=True)
            st.success("Saved and set as the active version.")
        except ValueError as e:
            st.error(f"Invalid input: {e}")

    act = db.active_materiality(c, eid)
    if act:
        st.subheader("Active materiality")
        m1, m2, m3 = st.columns(3)
        m1.metric("PM", f"{act['pm']:,.0f}")
        m2.metric("TE (performance)", f"{act['te']:,.0f}")
        m3.metric("SAD (clearly trivial)", f"{act['sad']:,.0f}")
        st.caption(f"Benchmark {act['benchmark_type']} x {act['percentage']:.1%} x "
                   f"adjustment {act['adjustment_factor']} - revision: {act['reason_for_revision']}")

    hist = db.read_table(c, "materiality_versions")
    if len(hist):
        st.subheader("Version history (is_active = 1 is the live version)")
        st.dataframe(hist[["version_id", "benchmark_type", "benchmark_amount",
                           "pm", "te", "sad", "reason_for_revision", "is_active"]],
                     use_container_width=True, hide_index=True)
    c.close()


# ============================================================ Page 3: Scoping
elif page == "3 - Scoping":
    st.title("3 - Scoping (Component & Account)")
    c = con()
    eid = first_engagement_id(c)
    if eid is None:
        st.warning("Please import an engagement on '1 - Upload Data' first.")
        st.stop()
    act = db.active_materiality(c, eid)
    if not act:
        st.warning("Please compute and save an active version on '2 - Materiality' first.")
        st.stop()

    te, sad = act["te"], act["sad"]
    st.caption(f"Using active materiality: TE {te:,.0f} - SAD {sad:,.0f}")

    if st.button("Run scoping engines", type="primary"):
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
        st.success("Scoping complete and written back to the database.")

    comp = db.read_table(c, "components")
    if len(comp) and comp["scope_decision"].notna().any():
        st.subheader("Component scope")
        n_full = (comp["scope_decision"] == "Full Scope").sum()
        st.caption(f"Full-scope components: {n_full} / {len(comp)}")
        st.dataframe(comp[["entity_name", "revenue", "pbt", "risk_rating",
                           "contribution_pct", "scope_decision", "scope_reason"]],
                     use_container_width=True, hide_index=True)

    acc = db.read_table(c, "accounts")
    if len(acc) and acc["testing_type"].notna().any():
        st.subheader("Account scope")
        n_test = (acc["testing_required"] == 1).sum()
        st.caption(f"Accounts requiring testing: {n_test} / {len(acc)}")
        st.dataframe(acc[["entity_id", "account_name", "account_type", "balance",
                          "risk_rating", "testing_required", "testing_type",
                          "testing_reason"]],
                     use_container_width=True, hide_index=True)
    c.close()
