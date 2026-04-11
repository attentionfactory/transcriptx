"""
database.py — SQLite: users + credits + auth
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "transcriptx.db")

PLANS = {
    "free":    {"credits": 3,  "batch": False, "csv_export": False, "name": "Free"},
    "starter": {"credits": 50, "batch": True,  "csv_export": True, "name": "Starter"},
    "pro":     {"credits": -1, "batch": True,  "csv_export": True, "name": "Pro"},  # -1 = unlimited
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
        db.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                event_id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
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
        ("billing_state", "TEXT DEFAULT 'none'"),
        ("grace_until", "TEXT"),
        ("cancel_at_period_end", "INTEGER DEFAULT 0"),
        ("current_period_end", "TEXT"),
        ("last_billing_event_at", "TEXT"),
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


def _parse_iso_utc_naive(s):
    """Parse Polar ISO8601 timestamps to naive UTC for comparison with datetime.utcnow()."""
    if not s:
        return None
    s = str(s).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def effective_entitlement(user):
    """
    Compute effective plan for gating from stored plan + billing columns.

    State machine (billing_state):
    - none + starter/pro: legacy rows → treat as active paid
    - active / uncanceled path: paid tier from plan when plan is starter/pro
    - past_due: paid while grace_until > now, else free
    - canceled (scheduled): paid while current_period_end > now, else free
    - revoked: free
    """
    if not user:
        return {
            "effective_plan": "free",
            "raw_plan": "free",
            "billing_state": "none",
            "has_paid_access": False,
        }

    raw = (user.get("plan") or "free").lower()
    bs = (user.get("billing_state") or "none").lower()
    now = datetime.utcnow()

    tier = raw if raw in ("starter", "pro") else "free"

    if bs == "revoked":
        return {
            "effective_plan": "free",
            "raw_plan": raw,
            "billing_state": "revoked",
            "has_paid_access": False,
        }

    if bs in ("none", ""):
        return {
            "effective_plan": tier if tier != "free" else "free",
            "raw_plan": raw,
            "billing_state": "none",
            "has_paid_access": tier != "free",
        }

    if bs == "past_due":
        gu = _parse_iso_utc_naive(user.get("grace_until"))
        if gu and gu > now and tier != "free":
            return {
                "effective_plan": tier,
                "raw_plan": raw,
                "billing_state": "past_due",
                "has_paid_access": True,
            }
        return {
            "effective_plan": "free",
            "raw_plan": raw,
            "billing_state": "past_due",
            "has_paid_access": False,
        }

    if bs == "canceled":
        if user.get("cancel_at_period_end"):
            end = _parse_iso_utc_naive(user.get("current_period_end")) or _parse_iso_utc_naive(
                user.get("ends_at")
            )
            if end and end > now and tier != "free":
                return {
                    "effective_plan": tier,
                    "raw_plan": raw,
                    "billing_state": "canceled",
                    "has_paid_access": True,
                }
        return {
            "effective_plan": "free",
            "raw_plan": raw,
            "billing_state": "canceled",
            "has_paid_access": False,
        }

    if bs == "active":
        return {
            "effective_plan": tier if tier != "free" else "free",
            "raw_plan": raw,
            "billing_state": "active",
            "has_paid_access": tier != "free",
        }

    # Unknown billing_state — fail closed (no paid access)
    return {
        "effective_plan": "free",
        "raw_plan": raw,
        "billing_state": bs,
        "has_paid_access": False,
    }


def _grace_until_from_subscription(sub):
    cpe = sub.get("current_period_end") or sub.get("ends_at")
    if cpe:
        return cpe
    days = int(os.environ.get("BILLING_GRACE_DAYS", "7"))
    return (datetime.utcnow() + timedelta(days=days)).isoformat()


def _extract_customer_from_subscription(sub):
    c = sub.get("customer") or {}
    polar_id = c.get("id") or sub.get("customer_id") or ""
    email = (c.get("email") or "").strip()
    return polar_id, email


def _upsert_subscription_user(
    db,
    polar_customer_id,
    email,
    plan_tier,
    *,
    billing_state,
    cancel_at_period_end=0,
    grace_until=None,
    current_period_end=None,
    last_event_iso=None,
):
    """Insert or update user row from Polar subscription sync."""
    last_event_iso = last_event_iso or datetime.utcnow().isoformat()
    cap = 1 if cancel_at_period_end else 0
    email_norm = email.lower().strip() if email else ""

    polar_row = db.execute(
        "SELECT id FROM users WHERE polar_customer_id = ?",
        (polar_customer_id,),
    ).fetchone()

    if polar_row:
        if email_norm:
            db.execute(
                """UPDATE users SET email = ?, plan = ?, billing_state = ?,
                   cancel_at_period_end = ?, grace_until = ?, current_period_end = ?,
                   last_billing_event_at = ?
                   WHERE polar_customer_id = ?""",
                (
                    email_norm,
                    plan_tier,
                    billing_state,
                    cap,
                    grace_until,
                    current_period_end,
                    last_event_iso,
                    polar_customer_id,
                ),
            )
        else:
            db.execute(
                """UPDATE users SET plan = ?, billing_state = ?,
                   cancel_at_period_end = ?, grace_until = ?, current_period_end = ?,
                   last_billing_event_at = ?
                   WHERE polar_customer_id = ?""",
                (
                    plan_tier,
                    billing_state,
                    cap,
                    grace_until,
                    current_period_end,
                    last_event_iso,
                    polar_customer_id,
                ),
            )
        return

    if email_norm:
        email_row = db.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?",
            (email_norm,),
        ).fetchone()
        if email_row:
            db.execute(
                """UPDATE users SET polar_customer_id = ?, plan = ?, billing_state = ?,
                   cancel_at_period_end = ?, grace_until = ?, current_period_end = ?,
                   last_billing_event_at = ?
                   WHERE id = ?""",
                (
                    polar_customer_id,
                    plan_tier,
                    billing_state,
                    cap,
                    grace_until,
                    current_period_end,
                    last_event_iso,
                    email_row["id"],
                ),
            )
            return

    if not email_norm:
        return

    reset_at = _next_reset_date()
    db.execute(
        """INSERT INTO users (polar_customer_id, email, plan, credits_used, credits_reset_at,
           billing_state, cancel_at_period_end, grace_until, current_period_end, last_billing_event_at)
           VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?)""",
        (
            polar_customer_id,
            email_norm,
            plan_tier,
            reset_at,
            billing_state,
            cap,
            grace_until,
            current_period_end,
            last_event_iso,
        ),
    )


def _revoke_polar_user(polar_customer_id):
    now = datetime.utcnow().isoformat()
    with get_db() as db:
        db.execute(
            """UPDATE users SET plan = 'free', billing_state = 'revoked',
               grace_until = NULL, cancel_at_period_end = 0, current_period_end = NULL,
               last_billing_event_at = ?
               WHERE polar_customer_id = ?""",
            (now, polar_customer_id),
        )


def sync_polar_subscription_webhook(event_type, event_data, plan_tier):
    """
    Apply Polar subscription webhook using subscription payload fields.
    plan_tier: starter|pro from product id mapping in app layer.
    """
    sub = event_data or {}
    polar_id, email = _extract_customer_from_subscription(sub)
    if not polar_id:
        return

    et = (event_type or "").lower()
    now_iso = datetime.utcnow().isoformat()
    status = (sub.get("status") or "").lower()
    cap = bool(sub.get("cancel_at_period_end"))
    cpe = sub.get("current_period_end") or sub.get("ends_at")

    if et == "subscription.revoked":
        _revoke_polar_user(polar_id)
        return

    if et == "subscription.uncanceled":
        with get_db() as db:
            _upsert_subscription_user(
                db,
                polar_id,
                email,
                plan_tier,
                billing_state="active",
                cancel_at_period_end=0,
                grace_until=None,
                current_period_end=cpe,
                last_event_iso=now_iso,
            )
        return

    if et == "subscription.canceled":
        if cap:
            with get_db() as db:
                _upsert_subscription_user(
                    db,
                    polar_id,
                    email,
                    plan_tier,
                    billing_state="canceled",
                    cancel_at_period_end=1,
                    grace_until=None,
                    current_period_end=cpe,
                    last_event_iso=now_iso,
                )
        else:
            _revoke_polar_user(polar_id)
        return

    if et == "subscription.past_due":
        grace = _grace_until_from_subscription(sub)
        with get_db() as db:
            _upsert_subscription_user(
                db,
                polar_id,
                email,
                plan_tier,
                billing_state="past_due",
                cancel_at_period_end=0,
                grace_until=grace,
                current_period_end=cpe,
                last_event_iso=now_iso,
            )
        return

    if et in (
        "subscription.created",
        "subscription.updated",
        "subscription.active",
    ):
        if status in ("incomplete", "incomplete_expired"):
            return

        if status in ("past_due", "unpaid"):
            grace = _grace_until_from_subscription(sub)
            with get_db() as db:
                _upsert_subscription_user(
                    db,
                    polar_id,
                    email,
                    plan_tier,
                    billing_state="past_due",
                    cancel_at_period_end=0,
                    grace_until=grace,
                    current_period_end=cpe,
                    last_event_iso=now_iso,
                )
            return

        if status == "canceled":
            if cap and cpe:
                with get_db() as db:
                    _upsert_subscription_user(
                        db,
                        polar_id,
                        email,
                        plan_tier,
                        billing_state="canceled",
                        cancel_at_period_end=1,
                        grace_until=None,
                        current_period_end=cpe,
                        last_event_iso=now_iso,
                    )
            else:
                _revoke_polar_user(polar_id)
            return

        if status in ("active", "trialing"):
            if cap:
                with get_db() as db:
                    _upsert_subscription_user(
                        db,
                        polar_id,
                        email,
                        plan_tier,
                        billing_state="canceled",
                        cancel_at_period_end=1,
                        grace_until=None,
                        current_period_end=cpe,
                        last_event_iso=now_iso,
                    )
            else:
                with get_db() as db:
                    _upsert_subscription_user(
                        db,
                        polar_id,
                        email,
                        plan_tier,
                        billing_state="active",
                        cancel_at_period_end=0,
                        grace_until=None,
                        current_period_end=cpe,
                        last_event_iso=now_iso,
                    )
            return


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

    ent = effective_entitlement(user)
    plan = PLANS.get(ent["effective_plan"], PLANS["free"])

    if plan["credits"] == -1:
        return -1

    return max(0, plan["credits"] - user["credits_used"])


def use_credit_for_user(user_id):
    """Deduct one credit. Returns True if successful."""
    user = get_user_by_id(user_id)
    if not user:
        return False

    ent = effective_entitlement(user)
    plan = PLANS.get(ent["effective_plan"], PLANS["free"])

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


def claim_webhook_event(event_id):
    """
    Atomically claim a webhook id before processing (idempotency / replay protection).
    Returns True if this is the first delivery, False if duplicate.
    """
    if not event_id:
        return False
    with get_db() as db:
        cur = db.execute(
            "INSERT OR IGNORE INTO webhook_events (event_id) VALUES (?)",
            (event_id,),
        )
        return cur.rowcount > 0


def release_webhook_event(event_id):
    """Remove claim so Polar retries can be reprocessed after an error."""
    if not event_id:
        return
    with get_db() as db:
        db.execute("DELETE FROM webhook_events WHERE event_id = ?", (event_id,))


# ── Polar linking ─────────────────────────────────────────

def link_polar_to_user(email, polar_customer_id, plan):
    """Attach polar_customer_id + plan to an existing user by email."""
    now = datetime.utcnow().isoformat()
    with get_db() as db:
        db.execute(
            """UPDATE users SET polar_customer_id = ?, plan = ?, billing_state = 'active',
               cancel_at_period_end = 0, grace_until = NULL, last_billing_event_at = ?
               WHERE LOWER(email) = ?""",
            (polar_customer_id, plan, now, email.lower().strip()),
        )


def create_or_update_user(polar_customer_id, email, plan):
    """Create or update a user from Polar webhook. Links to existing auth'd user if email matches."""
    now = datetime.utcnow().isoformat()
    with get_db() as db:
        # First: check if a user with this email already exists (from signup)
        email_row = db.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?",
            (email.lower().strip(),)
        ).fetchone()

        if email_row:
            db.execute(
                """UPDATE users SET polar_customer_id = ?, plan = ?, billing_state = 'active',
                   cancel_at_period_end = 0, grace_until = NULL, last_billing_event_at = ?
                   WHERE id = ?""",
                (polar_customer_id, plan, now, email_row["id"]),
            )
            return

        # Check if user exists by polar_customer_id
        polar_row = db.execute(
            "SELECT id FROM users WHERE polar_customer_id = ?",
            (polar_customer_id,)
        ).fetchone()

        if polar_row:
            db.execute(
                """UPDATE users SET email = ?, plan = ?, billing_state = 'active',
                   cancel_at_period_end = 0, grace_until = NULL, last_billing_event_at = ?
                   WHERE polar_customer_id = ?""",
                (email.lower().strip(), plan, now, polar_customer_id),
            )
        else:
            reset_at = _next_reset_date()
            db.execute(
                """INSERT INTO users (polar_customer_id, email, plan, credits_used, credits_reset_at,
                   billing_state, cancel_at_period_end, last_billing_event_at)
                   VALUES (?, ?, ?, 0, ?, 'active', 0, ?)""",
                (polar_customer_id, email.lower().strip(), plan, reset_at, now),
            )


def cancel_user(polar_customer_id):
    """Downgrade user to free on subscription cancel (immediate revoke)."""
    _revoke_polar_user(polar_customer_id)


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

    ent = effective_entitlement(user)
    plan = PLANS.get(ent["effective_plan"], PLANS["free"])
    if plan["credits"] == -1:
        return -1
    return max(0, plan["credits"] - user["credits_used"])


def use_user_credit(polar_customer_id):
    """Deduct one credit from a paid user (legacy)."""
    user = get_user(polar_customer_id)
    if not user:
        return False

    ent = effective_entitlement(user)
    plan = PLANS.get(ent["effective_plan"], PLANS["free"])

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
        rows = db.execute(
            "SELECT key, value FROM site_config WHERE key IN ('banner_enabled', 'banner_text', 'banner_json')"
        ).fetchall()
        d = {r["key"]: r["value"] for r in rows}
    fallback = {
        "enabled": d.get("banner_enabled", "0") == "1",
        "text": d.get("banner_text", ""),
        "cta": None,
        "dismissible": True,
    }
    raw = d.get("banner_json")
    if not raw:
        return fallback
    try:
        parsed = json.loads(raw)
    except Exception:
        return fallback

    if not isinstance(parsed, dict):
        return fallback

    cta = parsed.get("cta")
    if not isinstance(cta, dict):
        cta = None
    else:
        label = str(cta.get("label", "")).strip()
        url = str(cta.get("url", "")).strip()
        style = str(cta.get("style", "primary")).strip().lower()
        if not label or not url:
            cta = None
        else:
            if style not in ("primary", "ghost", "link"):
                style = "primary"
            cta = {"label": label, "url": url, "style": style}

    return {
        "enabled": bool(parsed.get("enabled", fallback["enabled"])),
        "text": str(parsed.get("text", fallback["text"])),
        "cta": cta,
        "dismissible": bool(parsed.get("dismissible", True)),
    }
