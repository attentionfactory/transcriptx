"""
database.py — SQLite: users + credits + auth
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
                email TEXT UNIQUE,
                password_hash TEXT,
                email_verified INTEGER DEFAULT 0,
                verify_code TEXT,
                verify_code_expires TEXT,
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
        db.execute("""
            CREATE TABLE IF NOT EXISTS site_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Migrate existing users table — add new auth columns if missing
        _migrate_columns(db)


def _migrate_columns(db):
    """Add new columns to existing users table if they don't exist."""
    existing = {row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()}
    migrations = [
        ("password_hash", "TEXT"),
        ("email_verified", "INTEGER DEFAULT 0"),
        ("verify_code", "TEXT"),
        ("verify_code_expires", "TEXT"),
    ]
    for col, col_type in migrations:
        if col not in existing:
            try:
                db.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    # Make email UNIQUE if it isn't already — SQLite can't ALTER constraints,
    # but we can add an index for lookup speed
    try:
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    except sqlite3.IntegrityError:
        pass  # duplicate emails exist — skip, we'll handle at app layer


# ── Auth ──────────────────────────────────────────────────

def create_user(email, password_hash):
    """Create a new user with email + hashed password. Returns user id or None if email taken."""
    with get_db() as db:
        try:
            reset_at = _next_reset_date()
            cursor = db.execute(
                "INSERT INTO users (email, password_hash, plan, credits_used, credits_reset_at) VALUES (?, ?, 'free', 0, ?)",
                (email.lower().strip(), password_hash, reset_at)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_user_by_email(email):
    """Lookup user by email (case-insensitive)."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?",
            (email.lower().strip(),)
        ).fetchone()
        if not row:
            return None
        user = dict(row)
        _maybe_reset_credits(db, user)
        return user


def get_user_by_id(user_id):
    """Lookup user by primary key id."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if not row:
            return None
        user = dict(row)
        _maybe_reset_credits(db, user)
        return user


def set_verify_code(email, code, expires):
    """Store OTP code + expiry for a user."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET verify_code = ?, verify_code_expires = ? WHERE LOWER(email) = ?",
            (code, expires, email.lower().strip())
        )


def verify_email(email, code):
    """Check OTP, mark email_verified, clear code. Returns user dict or None."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?",
            (email.lower().strip(),)
        ).fetchone()

        if not row:
            return None

        user = dict(row)

        if not user["verify_code"] or user["verify_code"] != code:
            return None

        if user["verify_code_expires"] and datetime.fromisoformat(user["verify_code_expires"]) < datetime.utcnow():
            return None

        db.execute(
            "UPDATE users SET email_verified = 1, verify_code = NULL, verify_code_expires = NULL WHERE id = ?",
            (user["id"],)
        )
        user["email_verified"] = 1
        return user


# ── Credits (unified — works by user id) ──────────────────

def get_credits_for_user(user_id):
    """Get remaining credits for any auth'd user."""
    user = get_user_by_id(user_id)
    if not user:
        return 0

    plan = PLANS.get(user["plan"], PLANS["free"])

    if plan["credits"] == -1:
        return -1

    return max(0, plan["credits"] - user["credits_used"])


def use_credit_for_user(user_id):
    """Deduct one credit. Returns True if successful."""
    user = get_user_by_id(user_id)
    if not user:
        return False

    plan = PLANS.get(user["plan"], PLANS["free"])

    if plan["credits"] == -1:
        with get_db() as db:
            db.execute(
                "UPDATE users SET credits_used = credits_used + 1 WHERE id = ?",
                (user_id,)
            )
        return True

    if user["credits_used"] >= plan["credits"]:
        return False

    with get_db() as db:
        db.execute(
            "UPDATE users SET credits_used = credits_used + 1 WHERE id = ?",
            (user_id,)
        )
    return True


def refund_credit_for_user(user_id):
    """Refund one credit after a failed transcription."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET credits_used = MAX(0, credits_used - 1) WHERE id = ?",
            (user_id,)
        )


def grant_credits(user_id, amount):
    """Grant credits by reducing credits_used (admin action)."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET credits_used = MAX(0, credits_used - ?) WHERE id = ?",
            (amount, user_id),
        )


# ── Polar linking ─────────────────────────────────────────

def link_polar_to_user(email, polar_customer_id, plan):
    """Attach polar_customer_id + plan to an existing user by email."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET polar_customer_id = ?, plan = ? WHERE LOWER(email) = ?",
            (polar_customer_id, plan, email.lower().strip())
        )


def create_or_update_user(polar_customer_id, email, plan):
    """Create or update a user from Polar webhook. Links to existing auth'd user if email matches."""
    with get_db() as db:
        # First: check if a user with this email already exists (from signup)
        email_row = db.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?",
            (email.lower().strip(),)
        ).fetchone()

        if email_row:
            db.execute(
                "UPDATE users SET polar_customer_id = ?, plan = ? WHERE id = ?",
                (polar_customer_id, plan, email_row["id"])
            )
            return

        # Check if user exists by polar_customer_id
        polar_row = db.execute(
            "SELECT id FROM users WHERE polar_customer_id = ?",
            (polar_customer_id,)
        ).fetchone()

        if polar_row:
            db.execute(
                "UPDATE users SET email = ?, plan = ? WHERE polar_customer_id = ?",
                (email.lower().strip(), plan, polar_customer_id)
            )
        else:
            reset_at = _next_reset_date()
            db.execute(
                "INSERT INTO users (polar_customer_id, email, plan, credits_used, credits_reset_at) VALUES (?, ?, ?, 0, ?)",
                (polar_customer_id, email.lower().strip(), plan, reset_at)
            )


def cancel_user(polar_customer_id):
    """Downgrade user to free on subscription cancel."""
    with get_db() as db:
        db.execute(
            "UPDATE users SET plan = 'free' WHERE polar_customer_id = ?",
            (polar_customer_id,)
        )


# ── Legacy functions (kept for backward compat) ──────────

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
        _maybe_reset_credits(db, user)
        return user


def get_user_credits(polar_customer_id):
    """Get remaining credits for a paid user (legacy)."""
    user = get_user(polar_customer_id)
    if not user:
        return 0

    plan = PLANS.get(user["plan"], PLANS["free"])
    if plan["credits"] == -1:
        return -1
    return max(0, plan["credits"] - user["credits_used"])


def use_user_credit(polar_customer_id):
    """Deduct one credit from a paid user (legacy)."""
    user = get_user(polar_customer_id)
    if not user:
        return False

    plan = PLANS.get(user["plan"], PLANS["free"])

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


# ── Free tier (session-based, legacy) ─────────────────────

def get_free_credits(session_id):
    """Get remaining free credits for an anonymous session."""
    with get_db() as db:
        row = db.execute(
            "SELECT credits_used, credits_reset_at FROM free_sessions WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if not row:
            reset_at = _next_reset_date()
            db.execute(
                "INSERT INTO free_sessions (session_id, credits_used, credits_reset_at) VALUES (?, 0, ?)",
                (session_id, reset_at)
            )
            return PLANS["free"]["credits"]

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


# ── Helpers ───────────────────────────────────────────────

def _maybe_reset_credits(db, user):
    """Reset credits if past reset date. Mutates user dict in-place."""
    if user["credits_reset_at"] and datetime.fromisoformat(user["credits_reset_at"]) <= datetime.utcnow():
        reset_at = _next_reset_date()
        db.execute(
            "UPDATE users SET credits_used = 0, credits_reset_at = ? WHERE id = ?",
            (reset_at, user["id"])
        )
        user["credits_used"] = 0
        user["credits_reset_at"] = reset_at


def _next_reset_date():
    """Next monthly reset (30 days from now)."""
    return (datetime.utcnow() + timedelta(days=30)).isoformat()


# ── Site config ───────────────────────────────────────────

def get_config(key, default=None):
    with get_db() as db:
        row = db.execute("SELECT value FROM site_config WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_config(key, value):
    with get_db() as db:
        db.execute(
            "INSERT INTO site_config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, value, value)
        )


def get_banner():
    with get_db() as db:
        rows = db.execute("SELECT key, value FROM site_config WHERE key IN ('banner_enabled', 'banner_text')").fetchall()
        d = {r["key"]: r["value"] for r in rows}
    return {
        "enabled": d.get("banner_enabled", "0") == "1",
        "text": d.get("banner_text", ""),
    }
