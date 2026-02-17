"""
database.py — SQLite: users + credits
"""

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "transcriptx.db")

PLANS = {
    "free":    {"credits": 3,  "batch": False, "csv_export": False},
    "starter": {"credits": 50, "batch": True,  "csv_export": True},
    "pro":     {"credits": -1, "batch": True,  "csv_export": True},  # -1 = unlimited
}


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                polar_customer_id TEXT UNIQUE,
                email TEXT,
                plan TEXT DEFAULT 'free',
                credits_used INTEGER DEFAULT 0,
                credits_reset_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS free_sessions (
                session_id TEXT PRIMARY KEY,
                credits_used INTEGER DEFAULT 0,
                credits_reset_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ── Free tier (session-based) ──────────────────────────────

def get_free_credits(session_id):
    """Get remaining free credits for an anonymous session."""
    with get_db() as db:
        row = db.execute(
            "SELECT credits_used, credits_reset_at FROM free_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if not row:
            # New session
            reset_at = _next_reset_date()
            db.execute(
                "INSERT INTO free_sessions (session_id, credits_used, credits_reset_at) VALUES (?, 0, ?)",
                (session_id, reset_at)
            )
            return PLANS["free"]["credits"]

        # Check if credits should reset
        if row["credits_reset_at"] and datetime.fromisoformat(row["credits_reset_at"]) <= datetime.utcnow():
            reset_at = _next_reset_date()
            db.execute(
                "UPDATE free_sessions SET credits_used = 0, credits_reset_at = ? WHERE session_id = ?",
                (reset_at, session_id)
            )
            return PLANS["free"]["credits"]

        return max(0, PLANS["free"]["credits"] - row["credits_used"])


def use_free_credit(session_id):
    """Deduct one free credit. Returns True if successful, False if out."""
    remaining = get_free_credits(session_id)
    if remaining <= 0:
        return False

    with get_db() as db:
        db.execute(
            "UPDATE free_sessions SET credits_used = credits_used + 1 WHERE session_id = ?",
            (session_id,)
        )
    return True


# ── Paid users (Polar-linked) ──────────────────────────────

def create_or_update_user(polar_customer_id, email, plan):
    """Create or update a user from Polar webhook."""
    with get_db() as db:
        existing = db.execute(
            "SELECT id FROM users WHERE polar_customer_id = ?",
            (polar_customer_id,)
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE users SET email = ?, plan = ? WHERE polar_customer_id = ?",
                (email, plan, polar_customer_id)
            )
        else:
            reset_at = _next_reset_date()
            db.execute(
                "INSERT INTO users (polar_customer_id, email, plan, credits_used, credits_reset_at) VALUES (?, ?, ?, 0, ?)",
                (polar_customer_id, email, plan, reset_at)
            )


def cancel_user(polar_customer_id):
    """Downgrade user to free on subscription cancel."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET plan = 'free' WHERE polar_customer_id = ?",
            (polar_customer_id,)
        )


def get_user(polar_customer_id):
    """Get user by Polar customer ID."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE polar_customer_id = ?",
            (polar_customer_id,)
        ).fetchone()

        if not row:
            return None

        user = dict(row)

        # Check if credits should reset
        if user["credits_reset_at"] and datetime.fromisoformat(user["credits_reset_at"]) <= datetime.utcnow():
            reset_at = _next_reset_date()
            db.execute(
                "UPDATE users SET credits_used = 0, credits_reset_at = ? WHERE polar_customer_id = ?",
                (reset_at, polar_customer_id)
            )
            user["credits_used"] = 0
            user["credits_reset_at"] = reset_at

        return user


def get_user_credits(polar_customer_id):
    """Get remaining credits for a paid user."""
    user = get_user(polar_customer_id)
    if not user:
        return 0

    plan = PLANS.get(user["plan"], PLANS["free"])

    # Unlimited
    if plan["credits"] == -1:
        return -1

    return max(0, plan["credits"] - user["credits_used"])


def use_user_credit(polar_customer_id):
    """Deduct one credit from a paid user. Returns True if successful."""
    user = get_user(polar_customer_id)
    if not user:
        return False

    plan = PLANS.get(user["plan"], PLANS["free"])

    # Unlimited plan
    if plan["credits"] == -1:
        with get_db() as db:
            db.execute(
                "UPDATE users SET credits_used = credits_used + 1 WHERE polar_customer_id = ?",
                (polar_customer_id,)
            )
        return True

    if user["credits_used"] >= plan["credits"]:
        return False

    with get_db() as db:
        db.execute(
            "UPDATE users SET credits_used = credits_used + 1 WHERE polar_customer_id = ?",
            (polar_customer_id,)
        )
    return True


def _next_reset_date():
    """Next monthly reset (30 days from now)."""
    return (datetime.utcnow() + timedelta(days=30)).isoformat()
