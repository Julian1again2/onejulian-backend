from pathlib import Path
from fastapi import APIRouter
import sqlite3

from policy_bundle import init_db, evaluate_policy, ingest_signal_and_maybe_promote

router = APIRouter(prefix="/api/v1/policy", tags=["policy"])

DB_PATH = Path(__file__).resolve().parent / "policy.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    conn.row_factory = sqlite3.Row
    return conn

def _load_active_rules(conn):
    rows = conn.execute(
        """
        SELECT id, rule_key, name, scope, action, priority, status
        FROM policy_rules
        WHERE status = 'active'
        ORDER BY priority DESC, id ASC
        """
    ).fetchall()

    rules = []
    for row in rows:
        rules.append(
            {
                "version_id": row["id"],
                "rule_key": row["rule_key"],
                "name": row["name"],
                "scope": row["scope"] or "payment",
                "priority": row["priority"] or 0,
                "action": row["action"],
                "condition": {},
                "status": row["status"],
            }
        )

    if rules:
        return rules

    return [
        {"version_id": 1, "scope": "payment", "priority": 10, "action": "review", "condition": {"country": "US"}},
        {"version_id": 2, "scope": "payment", "priority": 5, "action": "allow", "condition": {}},
    ]

@router.post("/evaluate")
def evaluate(event: dict):
    conn = _conn()
    try:
        rules = _load_active_rules(conn)
    finally:
        conn.close()

    result = evaluate_policy(event, rules, {"open_payments": 0})
    return result.model_dump() if hasattr(result, "model_dump") else result.__dict__

@router.post("/learn")
def learn(signal: dict):
    history = signal.pop("history", []) if isinstance(signal, dict) else []
    conn = _conn()
    try:
        return ingest_signal_and_maybe_promote(conn, signal, history)
    finally:
        conn.close()
