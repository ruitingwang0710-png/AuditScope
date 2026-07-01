"""
db.py - SQLite data layer
=========================
Creates the tables from DATA_MODEL.md and provides: initialisation, CSV
(DataFrame) import, writing decisions back, and reads. Uses only the standard
library sqlite3 plus pandas. Default database file: auditscope.db (git-ignored).
"""
from __future__ import annotations

import os
import sqlite3
from typing import Iterable

import pandas as pd

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "auditscope.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS engagements (
    engagement_id   INTEGER PRIMARY KEY,
    group_name      TEXT, financial_year INTEGER, currency TEXT,
    industry        TEXT, risk_level TEXT, prepared_by TEXT, reviewed_by TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS materiality_versions (
    version_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    engagement_id   INTEGER, benchmark_type TEXT, benchmark_amount REAL,
    percentage REAL, adjustment_factor REAL, te_percentage REAL, sad_percentage REAL,
    pm REAL, te REAL, sad REAL, reason_for_revision TEXT,
    is_active INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS components (
    entity_id INTEGER PRIMARY KEY, engagement_id INTEGER, entity_name TEXT,
    revenue REAL, pbt REAL, assets REAL, liabilities REAL, risk_rating TEXT,
    prior_year_adjustment REAL,
    contribution_pct REAL, scope_decision TEXT, scope_reason TEXT
);
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY, entity_id INTEGER, account_code TEXT,
    account_name TEXT, account_type TEXT, balance REAL, movement REAL,
    risk_rating TEXT,
    testing_required INTEGER, testing_type TEXT, testing_reason TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY, entity_id INTEGER, account_code TEXT,
    transaction_date TEXT, document_number TEXT, invoice_number TEXT,
    contract_number TEXT, bank_reference_number TEXT, counterparty_id TEXT,
    amount REAL, currency TEXT, debit_account TEXT, credit_account TEXT,
    transaction_hash TEXT
);
CREATE TABLE IF NOT EXISTS samples (
    sample_id INTEGER PRIMARY KEY AUTOINCREMENT, engagement_id INTEGER,
    entity_id INTEGER, account_code TEXT, transaction_hash TEXT,
    sample_type TEXT, selection_reason TEXT, selected_by TEXT,
    selected_at TEXT, testing_status TEXT, reuse_status TEXT
);
CREATE TABLE IF NOT EXISTS evidence_tests (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_hash TEXT,
    tested_account TEXT, assertion TEXT, evidence_type TEXT,
    evidence_reference TEXT, test_result TEXT, prepared_by TEXT,
    reviewed_by TEXT, test_date TEXT
);
CREATE TABLE IF NOT EXISTS assertion_requirements (
    req_id INTEGER PRIMARY KEY AUTOINCREMENT, account_type TEXT,
    assertion TEXT, is_required INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT, engagement_id INTEGER,
    transaction_hash TEXT, alert_type TEXT, severity TEXT, alert_score REAL,
    description TEXT, recommended_action TEXT, created_at TEXT DEFAULT (datetime('now'))
);
"""


def connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_db(db_path: str = DEFAULT_DB) -> None:
    con = connect(db_path)
    con.executescript(SCHEMA)
    con.commit()
    con.close()


# -- import -------------------------------------------------------------------
def _import_df(con, df: pd.DataFrame, table: str, cols: Iterable[str]) -> int:
    keep = [c for c in cols if c in df.columns]
    df[keep].to_sql(table, con, if_exists="append", index=False)
    return len(df)


def load_engagements(con, df) -> int:
    return _import_df(con, df, "engagements",
                      ["engagement_id", "group_name", "financial_year", "currency",
                       "industry", "risk_level", "prepared_by", "reviewed_by"])


def load_components(con, df) -> int:
    return _import_df(con, df, "components",
                      ["entity_id", "engagement_id", "entity_name", "revenue", "pbt",
                       "assets", "liabilities", "risk_rating", "prior_year_adjustment"])


def load_accounts(con, df) -> int:
    return _import_df(con, df, "accounts",
                      ["account_id", "entity_id", "account_code", "account_name",
                       "account_type", "balance", "movement", "risk_rating"])


def load_transactions(con, df) -> int:
    return _import_df(con, df, "transactions",
                      ["transaction_id", "entity_id", "account_code", "transaction_date",
                       "document_number", "invoice_number", "contract_number",
                       "bank_reference_number", "counterparty_id", "amount", "currency",
                       "debit_account", "credit_account", "transaction_hash"])


def save_materiality_version(con, engagement_id: int, m: dict,
                             make_active: bool = True) -> int:
    """Insert one materiality version; if make_active, deactivate the others."""
    if make_active:
        con.execute("UPDATE materiality_versions SET is_active=0 WHERE engagement_id=?",
                    (engagement_id,))
    cur = con.execute(
        """INSERT INTO materiality_versions
           (engagement_id, benchmark_type, benchmark_amount, percentage,
            adjustment_factor, te_percentage, sad_percentage, pm, te, sad,
            reason_for_revision, is_active)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (engagement_id, m["benchmark_type"], m["benchmark_amount"], m["percentage"],
         m["adjustment_factor"], m["te_percentage"], m["sad_percentage"],
         m["pm"], m["te"], m["sad"], m.get("reason_for_revision", ""),
         1 if make_active else 0))
    con.commit()
    return cur.lastrowid


def active_materiality(con, engagement_id: int) -> dict | None:
    row = con.execute(
        "SELECT * FROM materiality_versions WHERE engagement_id=? AND is_active=1 "
        "ORDER BY version_id DESC LIMIT 1", (engagement_id,)).fetchone()
    if not row:
        return None
    cols = [d[0] for d in con.execute(
        "SELECT * FROM materiality_versions LIMIT 0").description]
    return dict(zip(cols, row))


def update_component_scope(con, entity_id: int, contribution_pct, decision, reason):
    con.execute("UPDATE components SET contribution_pct=?, scope_decision=?, "
                "scope_reason=? WHERE entity_id=?",
                (contribution_pct, decision, reason, entity_id))
    con.commit()


def update_account_scope(con, account_id: int, required, ttype, reason):
    con.execute("UPDATE accounts SET testing_required=?, testing_type=?, "
                "testing_reason=? WHERE account_id=?",
                (required, ttype, reason, account_id))
    con.commit()


def read_table(con, table: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {table}", con)
