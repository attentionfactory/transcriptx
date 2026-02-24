"""
app.py — TranscriptX
======================
Flask app with Polar payments, SQLite credits, Groq transcription.
Email + password + OTP auth via bcrypt + Resend.
"""

import os
import uuid
import json
import logging
import random
import re
import subprocess
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
from disposable_email_domains import blocklist as _disposable_pkg
from dotenv import load_dotenv

EXTRA_DISPOSABLE_DOMAINS = {
    "tempmail.com", "tempmail.io", "tempmail.net",
    "throwaway.email", "burnermail.io", "trashmailr.com",
    "temp-mail.io", "tempemail.cc", "tempemailco.com",
    "tempmailgen.com", "tempinboxmail.com", "tempm.com",
    "temporary.best", "temp.now", "disposablemail.com",
    "5minmail.com", "hour.email", "noemail.cc",
    "anonibox.com", "luxusmail.org", "mail7.app",
    "dmailpro.net", "adresseemailtemporaire.com",
    "emailtemporalgratis.com", "emailtemporanea.org",
}
disposable_domains = _disposable_pkg | EXTRA_DISPOSABLE_DOMAINS

load_dotenv()  # Load .env file automatically

import bcrypt
import requests as http_requests
from flask import Flask, request, jsonify, session, redirect, render_template_string, Response, stream_with_context, send_from_directory
from database import (
    init_db, PLANS,
    get_free_credits, use_free_credit,
    create_or_update_user, cancel_user, get_user, get_user_credits, use_user_credit,
    create_user, get_user_by_email, get_user_by_id,
    set_verify_code, verify_email,
    get_credits_for_user, use_credit_for_user, refund_credit_for_user,
    link_polar_to_user,
)
from transcribe import process_url

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-" + uuid.uuid4().hex)

# Polar config
POLAR_WEBHOOK_SECRET = os.environ.get("POLAR_WEBHOOK_SECRET", "")
POLAR_STARTER_PRODUCT_ID = os.environ.get("POLAR_STARTER_PRODUCT_ID", "")
POLAR_PRO_PRODUCT_ID = os.environ.get("POLAR_PRO_PRODUCT_ID", "")
POLAR_CHECKOUT_STARTER = os.environ.get("POLAR_CHECKOUT_STARTER", "#")
POLAR_CHECKOUT_PRO = os.environ.get("POLAR_CHECKOUT_PRO", "#")
POLAR_CUSTOMER_PORTAL = os.environ.get("POLAR_CUSTOMER_PORTAL", "#")

# Resend config
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "TranscriptX <onboarding@resend.dev>")

# Initialize DB on startup
init_db()


@app.route("/<path:filename>")
def serve_static_root(filename):
    """Serve favicon/manifest files from /static at root URLs."""
    allowed = {"favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
               "apple-touch-icon.png", "android-chrome-192x192.png",
               "android-chrome-512x512.png", "site.webmanifest"}
    if filename in allowed:
        return send_from_directory("static", filename)
    return ("Not found", 404)


# ── Helpers ─────────────────────────────────────────────────

def _get_session_id():
    """Get or create anonymous session ID."""
    if "sid" not in session:
        session["sid"] = uuid.uuid4().hex
    return session["sid"]


def _get_current_user():
    """Get current user info. Checks session['user_id'] first (auth'd user)."""
    user_id = session.get("user_id")

    if user_id:
        user = get_user_by_id(user_id)
        if user:
            plan = PLANS.get(user["plan"], PLANS["free"])
            credits = get_credits_for_user(user_id)
            return {
                "type": "paid" if user["plan"] != "free" else "authed_free",
                "user_id": user["id"],
                "email": user["email"],
                "plan": user["plan"],
                "plan_name": plan.get("name", user["plan"].title()),
                "credits": credits,
                "credits_label": "Unlimited" if credits == -1 else str(credits),
                "batch": plan["batch"],
                "csv_export": plan["csv_export"],
                "logged_in": True,
            }

    # Not logged in
    return {
        "type": "anonymous",
        "user_id": None,
        "email": None,
        "plan": "free",
        "plan_name": "Free",
        "credits": 0,
        "credits_label": "0",
        "batch": False,
        "csv_export": False,
        "logged_in": False,
    }


def _generate_otp():
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def _send_otp_email(email, code):
    """Send OTP via Resend API. Returns True on success."""
    if not RESEND_API_KEY:
        print(f"⚠️  RESEND_API_KEY not set. OTP for {email}: {code}")
        return True  # Dev mode — just print

    try:
        resp = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [email],
                "subject": f"TranscriptX — Your verification code is {code}",
                "html": f"""
                    <div style="font-family:monospace;max-width:400px;margin:0 auto;padding:2rem;">
                        <h2 style="margin:0 0 1rem;">TranscriptX</h2>
                        <p>Your verification code:</p>
                        <div style="font-size:2rem;font-weight:bold;letter-spacing:0.3em;padding:1rem;background:#f5f5f5;text-align:center;border-radius:8px;">{code}</div>
                        <p style="opacity:0.6;font-size:0.85rem;margin-top:1rem;">This code expires in 10 minutes.</p>
                    </div>
                """,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Resend error: {e}")
        return False


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


# ── API Routes ──────────────────────────────────────────────

@app.route("/api/extract", methods=["POST"])
def api_extract():
    """Extract transcript from a URL. Deducts 1 credit. Requires auth."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Please sign up or log in to transcribe."}), 401

    data = request.json or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"status": "error", "error": "No URL provided"}), 400

    if not url.startswith(("https://", "http://")):
        return jsonify({"status": "error", "error": "Invalid URL. Must start with https://"}), 400

    # Check + deduct credits
    if user["credits"] != -1 and user["credits"] <= 0:
        return jsonify({"status": "error", "error": "No credits remaining. Upgrade your plan!"}), 403
    if not use_credit_for_user(user["user_id"]):
        return jsonify({"status": "error", "error": "No credits remaining."}), 403

    # Process
    model = data.get("model", "whisper-large-v3-turbo")
    if model not in ("whisper-large-v3-turbo", "whisper-large-v3"):
        model = "whisper-large-v3-turbo"

    result = process_url(url, model=model)
    if result.get("status") == "error":
        refund_credit_for_user(user["user_id"])
    return jsonify(result)


@app.route("/api/profile-links")
def api_profile_links():
    """Stream video URLs from a profile using yt-dlp. 1 credit per 20 links."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"error": "Login required"}), 401

    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        limit = int(request.args.get("limit", "0"))
    except ValueError:
        limit = 0

    cmd = [
        "yt-dlp", "--flat-playlist", "--print", "url",
        "--no-warnings", "--no-download",
    ]
    if limit > 0:
        cmd += ["--playlist-end", str(limit)]
    cmd.append(url)

    user_id = user["user_id"]
    is_unlimited = user["credits"] == -1

    def generate():
        if not is_unlimited:
            if not use_credit_for_user(user_id):
                yield f"data: {json.dumps({'type':'error','msg':'No credits remaining.'})}\n\n"
                return
        credits_charged = 1

        proc = None
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1,
            )
            count = 0
            for line in proc.stdout:
                link = line.strip()
                if not link:
                    continue
                count += 1

                needed = (count + 4) // 5
                if needed > credits_charged and not is_unlimited:
                    if not use_credit_for_user(user_id):
                        yield f"data: {json.dumps({'type':'done','count':count - 1,'credits_used':credits_charged,'msg':'Credit limit reached'})}\n\n"
                        return
                    credits_charged = needed

                yield f"data: {json.dumps({'type':'link','url':link,'n':count})}\n\n"

            proc.wait()
            if count == 0:
                stderr = proc.stderr.read()
                if "login" in stderr.lower() or "cookie" in stderr.lower():
                    yield f"data: {json.dumps({'type':'error','msg':'This profile requires login/cookies. Try a public profile.'})}\n\n"
                else:
                    yield f"data: {json.dumps({'type':'error','msg': stderr[:200] or 'No videos found. Check the URL.'})}\n\n"
            else:
                yield f"data: {json.dumps({'type':'done','count':count,'credits_used':credits_charged})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','msg':str(e)})}\n\n"
        finally:
            if proc and proc.poll() is None:
                proc.kill()

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/me")
def api_me():
    """Get current user info + credits."""
    return jsonify(_get_current_user())


# ── Auth Routes ─────────────────────────────────────────────

@app.route("/api/signup", methods=["POST"])
def api_signup():
    """Register with email + password, send OTP."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not EMAIL_RE.match(email):
        return jsonify({"status": "error", "error": "Valid email required"}), 400
    if email.split("@")[1] in disposable_domains:
        return jsonify({"status": "error", "error": "Disposable email addresses are not allowed"}), 400
    if len(password) < 6:
        return jsonify({"status": "error", "error": "Password must be at least 6 characters"}), 400

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing and existing.get("email_verified"):
        return jsonify({"status": "error", "error": "Account already exists. Log in instead."}), 409
    if existing and not existing.get("email_verified"):
        # Re-signup for unverified account — update password + resend code
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        from database import get_db
        with get_db() as db:
            db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, existing["id"]))
        code = _generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        set_verify_code(email, code, expires)
        _send_otp_email(email, code)
        return jsonify({"status": "ok", "step": "verify"})

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = create_user(email, pw_hash)

    if not user_id:
        return jsonify({"status": "error", "error": "Account already exists."}), 409

    # Generate + send OTP
    code = _generate_otp()
    expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    set_verify_code(email, code, expires)
    _send_otp_email(email, code)

    return jsonify({"status": "ok", "step": "verify"})


@app.route("/api/verify", methods=["POST"])
def api_verify():
    """Verify OTP code, log user in."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()

    if not email or not code:
        return jsonify({"status": "error", "error": "Email and code required"}), 400

    user = verify_email(email, code)
    if not user:
        return jsonify({"status": "error", "error": "Invalid or expired code"}), 400

    session["user_id"] = user["id"]
    session.pop("polar_customer_id", None)  # clean up legacy
    return jsonify({"status": "ok"})


@app.route("/api/resend-code", methods=["POST"])
def api_resend_code():
    """Resend OTP to email."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"status": "error", "error": "Email required"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"status": "error", "error": "No account found"}), 404

    code = _generate_otp()
    expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    set_verify_code(email, code, expires)
    _send_otp_email(email, code)

    return jsonify({"status": "ok"})


# ── Polar Webhooks ──────────────────────────────────────────

@app.route("/webhooks/polar", methods=["POST"])
def polar_webhook():
    """
    Handle Polar subscription events.
    Links polar_customer_id to existing auth'd user by email.
    """
    payload = request.get_data()

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    event_type = data.get("type", "")
    event_data = data.get("data", {})

    if event_type in ("subscription.created", "subscription.updated", "subscription.active"):
        customer = event_data.get("customer", {})
        polar_id = customer.get("id", "")
        email = customer.get("email", "")
        product = event_data.get("product", {})
        product_id = product.get("id", "")

        # Map product to plan
        if product_id == POLAR_PRO_PRODUCT_ID:
            plan = "pro"
        elif product_id == POLAR_STARTER_PRODUCT_ID:
            plan = "starter"
        else:
            plan = "starter"

        if polar_id:
            create_or_update_user(polar_id, email, plan)
            print(f"✅ User {email} → {plan}")

    elif event_type in ("subscription.canceled", "subscription.revoked"):
        customer = event_data.get("customer", {})
        polar_id = customer.get("id", "")
        if polar_id:
            cancel_user(polar_id)
            print(f"⬇️ User {polar_id} → free (canceled)")

    return "ok", 200


@app.route("/auth/polar/callback")
def polar_callback():
    """After Polar checkout, link the Polar customer to the logged-in user."""
    customer_id = request.args.get("customer_id", "")
    user_id = session.get("user_id")

    if customer_id and user_id:
        user = get_user_by_id(user_id)
        if user:
            link_polar_to_user(user["email"], customer_id, user.get("plan", "starter"))

    return redirect("/")


@app.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate with email + password."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email:
        return jsonify({"status": "error", "error": "Enter your email"}), 400
    if not password:
        return jsonify({"status": "error", "error": "Enter your password"}), 400

    user = get_user_by_email(email)

    if not user or not user.get("password_hash"):
        return jsonify({"status": "error", "error": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify({"status": "error", "error": "Invalid email or password"}), 401

    if not user.get("email_verified"):
        # Resend OTP automatically
        code = _generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        set_verify_code(email, code, expires)
        _send_otp_email(email, code)
        return jsonify({"status": "verify", "error": "Email not verified. Code sent."}), 200

    session["user_id"] = user["id"]
    return jsonify({"status": "ok", "plan": user["plan"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Clear session."""
    session.pop("user_id", None)
    session.pop("polar_customer_id", None)
    return jsonify({"status": "ok"})


# ── Admin ───────────────────────────────────────────────────

ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]

@app.route("/admin")
def admin():
    """Admin dashboard — protected by login+email whitelist OR ?key= param."""
    user = _get_current_user()
    has_admin_email = user["logged_in"] and user.get("email", "").lower() in ADMIN_EMAILS
    has_admin_key = request.args.get("key") == ADMIN_KEY
    if not has_admin_email and not has_admin_key:
        return "Not found", 404

    from database import get_db
    with get_db() as db:
        users = [dict(r) for r in db.execute(
            "SELECT polar_customer_id, email, plan, credits_used, credits_reset_at, created_at FROM users WHERE plan != 'free' ORDER BY created_at DESC"
        ).fetchall()]

        free_users = [dict(r) for r in db.execute(
            "SELECT id, email, credits_used, credits_reset_at, created_at FROM users WHERE plan = 'free' AND email_verified = 1 ORDER BY created_at DESC LIMIT 100"
        ).fetchall()]

        stats = {
            "total_users": db.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1").fetchone()[0],
            "paid_users": db.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'").fetchone()[0],
            "starter": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'starter'").fetchone()[0],
            "pro": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'pro'").fetchone()[0],
            "free_users": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'free' AND email_verified = 1").fetchone()[0],
            "total_free_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM users WHERE plan = 'free'").fetchone()[0],
            "total_paid_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM users WHERE plan != 'free'").fetchone()[0],
        }

    return render_template_string(ADMIN_TEMPLATE, users=users, free_users=free_users, stats=stats)


ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Admin</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --red: #B84B3F;
            --green: #709472;
            --grey: #C4C5C7;
            --ink: #0a0a0a;
            --f-wide: 'Michroma', sans-serif;
            --f-tech: 'Space Mono', monospace;
            --radius: 2rem;
            --bw: 1.5px;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:var(--bg); color:var(--ink); font-family:var(--f-tech); line-height:1.4; }

        .layout { max-width:1100px; margin:0 auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; }

        .label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; opacity:0.6; display:block; }
        .panel { border-radius:var(--radius); padding:2rem; position:relative; overflow:hidden; }

        @keyframes slideUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:none; } }

        /* ── Nav ── */
        nav {
            display:flex; justify-content:space-between; align-items:center;
            padding:1rem 2rem; background:var(--grey); border-radius:100px;
        }
        .nav-logo { font-family:var(--f-wide); font-size:1.1rem; font-weight:900; text-decoration:none; color:var(--ink); }
        .nav-logo em { font-style:normal; font-size:0.5em; vertical-align:super; }
        .nav-right { display:flex; align-items:center; gap:0.8rem; }
        .nav-right a {
            color:var(--ink); text-decoration:none; font-size:0.7rem; font-weight:700;
            text-transform:uppercase; padding:0.5rem 1rem; border-radius:4px;
            border:1px solid transparent; transition:all 0.2s;
        }
        .nav-right a:hover { border-color:var(--ink); background:rgba(0,0,0,0.05); }
        .nav-badge {
            font-size:0.6rem; padding:0.4rem 0.8rem; border-radius:4px;
            font-weight:700; text-transform:uppercase; background:rgba(0,0,0,0.08);
        }

        /* ── Revenue ── */
        .revenue { background:var(--green); display:flex; align-items:center; justify-content:space-between; animation:slideUp 0.4s ease both; }
        .revenue-amount { font-family:var(--f-wide); font-size:2rem; }
        .revenue-amount .currency { font-size:1.2rem; }
        .revenue-label { font-size:0.65rem; opacity:0.6; text-transform:uppercase; letter-spacing:0.05em; margin-top:4px; }
        .revenue-breakdown { font-size:0.7rem; text-align:right; line-height:2; }
        .revenue-breakdown strong { font-weight:700; }

        /* ── Stats ── */
        .stats-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }
        .stat-card {
            background:var(--grey); border-radius:var(--radius); padding:1.5rem; text-align:center;
            animation:slideUp 0.4s ease both;
        }
        .stat-card:nth-child(1) { animation-delay:0.05s; }
        .stat-card:nth-child(2) { animation-delay:0.1s; }
        .stat-card:nth-child(3) { animation-delay:0.15s; }
        .stat-card:nth-child(4) { animation-delay:0.2s; }
        .stat-card:nth-child(5) { animation-delay:0.25s; }
        .stat-card:nth-child(6) { animation-delay:0.3s; }
        .stat-num {
            font-family:var(--f-wide); font-size:1.6rem;
            font-variant-numeric:tabular-nums; margin-bottom:4px;
        }
        .stat-lbl { font-size:0.55rem; text-transform:uppercase; letter-spacing:1.5px; opacity:0.5; }

        /* ── Charts ── */
        .chart-row { display:flex; gap:1rem; animation:slideUp 0.4s 0.3s ease both; }
        .chart-card {
            background:var(--grey); border-radius:var(--radius); padding:1.5rem;
            flex:1; display:flex; align-items:center; gap:1.2rem;
        }
        .circle-wrap { width:70px; height:70px; position:relative; flex-shrink:0; }
        .circle-bg { fill:none; stroke:rgba(0,0,0,0.1); stroke-width:6; }
        .circle-fg {
            fill:none; stroke-width:6; stroke-linecap:round;
            transform:rotate(-90deg); transform-origin:center;
            transition:stroke-dashoffset 1.5s ease;
        }
        .circle-fg.orange { stroke:var(--orange); }
        .circle-fg.green { stroke:var(--green); }
        .circle-label {
            position:absolute; inset:0; display:flex; align-items:center;
            justify-content:center; font-size:0.8rem; font-weight:700;
        }
        .chart-title { font-family:var(--f-wide); font-size:0.65rem; text-transform:uppercase; margin-bottom:4px; }
        .chart-sub { font-size:0.7rem; opacity:0.6; }

        /* ── Section head ── */
        .section-head {
            display:flex; align-items:center; justify-content:space-between;
            color:var(--grey); padding:0 0.5rem; animation:slideUp 0.4s 0.35s ease both;
        }
        .section-title { font-family:var(--f-wide); font-size:0.75rem; text-transform:uppercase; }
        .section-count {
            font-size:0.6rem; padding:0.3rem 0.7rem; border:var(--bw) solid var(--grey);
            color:var(--grey); text-transform:uppercase;
        }

        /* ── Tables ── */
        .table-wrap {
            background:var(--grey); border-radius:var(--radius); overflow:hidden;
            animation:slideUp 0.4s 0.4s ease both;
        }
        table { width:100%; border-collapse:collapse; }
        thead { background:rgba(0,0,0,0.05); }
        th {
            text-align:left; padding:1rem 1.2rem; font-size:0.55rem; font-weight:700;
            text-transform:uppercase; letter-spacing:1.2px; opacity:0.5;
        }
        td {
            padding:0.8rem 1.2rem; font-size:0.75rem;
            border-top:var(--bw) solid rgba(0,0,0,0.08); vertical-align:middle;
        }
        tr:hover td { background:rgba(0,0,0,0.03); }
        .email-cell { font-weight:700; }

        .badge {
            display:inline-flex; align-items:center; gap:5px;
            padding:4px 10px; font-size:0.55rem; font-weight:700;
            text-transform:uppercase; letter-spacing:0.5px; border:var(--bw) solid var(--ink);
        }
        .badge::before { content:''; width:6px; height:6px; border-radius:50%; }
        .badge.starter { border-color:var(--orange); }
        .badge.starter::before { background:var(--orange); }
        .badge.pro { border-color:var(--green); }
        .badge.pro::before { background:var(--green); }
        .badge.free { border-color:rgba(0,0,0,0.3); }
        .badge.free::before { background:rgba(0,0,0,0.3); }

        .mono { font-size:0.7rem; opacity:0.5; }
        .usage-bar-wrap { display:flex; align-items:center; gap:8px; }
        .usage-bar { width:50px; height:3px; background:rgba(0,0,0,0.12); overflow:hidden; }
        .usage-bar-fill { height:100%; transition:width 1s ease; }
        .usage-bar-fill.orange { background:var(--orange); }
        .usage-bar-fill.green { background:var(--green); }
        .usage-bar-fill.red { background:var(--red); }

        .empty-row { text-align:center; opacity:0.4; padding:2rem 1rem; font-size:0.75rem; }

        /* ── Footer ── */
        .tech-footer {
            border:1px solid #333; color:#555; padding:1.5rem 2rem; font-size:0.6rem;
            text-transform:uppercase; display:flex; justify-content:space-between; letter-spacing:0.05em;
        }

        @media (max-width:700px) {
            .layout { padding:0.6rem; gap:0.6rem; }
            .revenue { flex-direction:column; gap:1rem; text-align:center; border-radius:1.2rem; padding:1.5rem; }
            .revenue-breakdown { text-align:center; }
            .stats-grid { grid-template-columns:repeat(2,1fr); gap:0.6rem; }
            .stat-card { border-radius:1.2rem; padding:1.2rem; }
            .chart-row { flex-direction:column; }
            .chart-card { border-radius:1.2rem; }
            .table-wrap { border-radius:1.2rem; }
            .section-head { padding:0 0.3rem; }
            .tech-footer { flex-direction:column; gap:0.8rem; text-align:center; padding:1rem; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <!-- Nav -->
        <nav>
            <a class="nav-logo" href="/">TRANSCRIPTX<em>&reg;</em></a>
            <div class="nav-right">
                <span class="nav-badge">Admin</span>
                <a href="/">← App</a>
            </div>
        </nav>

        <!-- Revenue -->
        <div class="panel revenue">
            <div>
                <div class="revenue-amount"><span class="currency">$</span>{{ stats.starter * 2 + stats.pro * 4 }}</div>
                <div class="revenue-label">Estimated MRR</div>
            </div>
            <div class="revenue-breakdown">
                <div><strong>{{ stats.starter }}</strong> Starter &times; $2</div>
                <div><strong>{{ stats.pro }}</strong> Pro &times; $4</div>
                <div><strong>{{ stats.total_paid_transcripts + stats.total_free_transcripts }}</strong> total transcripts</div>
            </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.paid_users }}">0</div>
                <div class="stat-lbl">Paid Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.starter }}">0</div>
                <div class="stat-lbl">Starter</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.pro }}">0</div>
                <div class="stat-lbl">Pro</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.free_users }}">0</div>
                <div class="stat-lbl">Free Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.total_paid_transcripts }}">0</div>
                <div class="stat-lbl">Paid Transcripts</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.total_free_transcripts }}">0</div>
                <div class="stat-lbl">Free Transcripts</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="chart-row">
            <div class="chart-card">
                <div class="circle-wrap">
                    <svg viewBox="0 0 36 36" width="70" height="70">
                        <circle class="circle-bg" cx="18" cy="18" r="15.9"/>
                        <circle class="circle-fg orange" cx="18" cy="18" r="15.9"
                            stroke-dasharray="100"
                            stroke-dashoffset="{{ 100 - ([((stats.paid_users / (stats.paid_users + stats.free_users)) * 100) if (stats.paid_users + stats.free_users) > 0 else 0, 100] | min) }}"/>
                    </svg>
                    <div class="circle-label">{{ ((stats.paid_users / (stats.paid_users + stats.free_users)) * 100) | int if (stats.paid_users + stats.free_users) > 0 else 0 }}%</div>
                </div>
                <div>
                    <div class="chart-title">Conversion Rate</div>
                    <div class="chart-sub">{{ stats.paid_users }} paid / {{ stats.paid_users + stats.free_users }} total</div>
                </div>
            </div>
            <div class="chart-card">
                <div class="circle-wrap">
                    <svg viewBox="0 0 36 36" width="70" height="70">
                        <circle class="circle-bg" cx="18" cy="18" r="15.9"/>
                        <circle class="circle-fg green" cx="18" cy="18" r="15.9"
                            stroke-dasharray="100"
                            stroke-dashoffset="{{ 100 - ([((stats.pro / stats.paid_users) * 100) if stats.paid_users > 0 else 0, 100] | min) }}"/>
                    </svg>
                    <div class="circle-label">{{ ((stats.pro / stats.paid_users) * 100) | int if stats.paid_users > 0 else 0 }}%</div>
                </div>
                <div>
                    <div class="chart-title">Pro Upgrade Rate</div>
                    <div class="chart-sub">{{ stats.pro }} Pro / {{ stats.paid_users }} paid</div>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div class="section-head">
            <div class="section-title">Paid Users</div>
            <div class="section-count">{{ stats.total_users }}</div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr><th>Email</th><th>Plan</th><th>Usage</th><th>Since</th></tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td class="email-cell">{{ u.email or '—' }}</td>
                        <td><span class="badge {{ u.plan }}">{{ u.plan }}</span></td>
                        <td>
                            <div class="usage-bar-wrap">
                                <span class="mono">{{ u.credits_used }}</span>
                                {% if u.plan == 'pro' %}
                                <div class="usage-bar"><div class="usage-bar-fill green" style="width:100%"></div></div>
                                <span class="mono">&infin;</span>
                                {% elif u.plan == 'starter' %}
                                <div class="usage-bar"><div class="usage-bar-fill orange" style="width:{{ (u.credits_used / 50 * 100) | int }}%"></div></div>
                                <span class="mono">/ 50</span>
                                {% else %}
                                <div class="usage-bar"><div class="usage-bar-fill red" style="width:{{ (u.credits_used / 3 * 100) | int }}%"></div></div>
                                <span class="mono">/ 3</span>
                                {% endif %}
                            </div>
                        </td>
                        <td class="mono">{{ u.created_at[:10] if u.created_at else '—' }}</td>
                    </tr>
                    {% endfor %}
                    {% if not users %}<tr><td colspan="4" class="empty-row">No users yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>

        <!-- Free Users -->
        <div class="section-head">
            <div class="section-title">Free Users</div>
            <div class="section-count">{{ stats.free_users }}</div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr><th>Email</th><th>Usage</th><th>Resets</th><th>Joined</th></tr>
                </thead>
                <tbody>
                    {% for u in free_users %}
                    <tr>
                        <td class="email-cell">{{ u.email or '—' }}</td>
                        <td>
                            <div class="usage-bar-wrap">
                                <span class="mono">{{ u.credits_used }}</span>
                                <div class="usage-bar"><div class="usage-bar-fill orange" style="width:{{ (u.credits_used / 3 * 100) | int }}%"></div></div>
                                <span class="mono">/ 3</span>
                            </div>
                        </td>
                        <td class="mono">{{ u.credits_reset_at[:10] if u.credits_reset_at else '—' }}</td>
                        <td class="mono">{{ u.created_at[:10] if u.created_at else '—' }}</td>
                    </tr>
                    {% endfor %}
                    {% if not free_users %}<tr><td colspan="4" class="empty-row">No free users yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <footer class="tech-footer">
            <div>TranscriptX Admin<br>System Dashboard</div>
            <div style="text-align:right;">Built by <a href="https://google.com">x362 IIC</a></div>
        </footer>
    </div>

    <script>
        document.querySelectorAll('[data-count]').forEach(el => {
            const target = parseInt(el.dataset.count);
            if (target === 0) return;
            let count = 0;
            const step = Math.max(1, Math.ceil(target / 40));
            const interval = setInterval(() => {
                count = Math.min(count + step, target);
                el.textContent = count;
                if (count >= target) clearInterval(interval);
            }, 32);
        });
    </script>
</body>
</html>
"""


# ── UI ──────────────────────────────────────────────────────

@app.route("/")
def index():
    user = _get_current_user()
    return render_template_string(HTML_TEMPLATE, user=user, config={
        "checkout_starter": POLAR_CHECKOUT_STARTER,
        "checkout_pro": POLAR_CHECKOUT_PRO,
        "customer_portal": POLAR_CUSTOMER_PORTAL,
    })


@app.route("/pricing")
def pricing():
    user = _get_current_user()
    return render_template_string(PRICING_TEMPLATE, user=user, config={
        "checkout_starter": POLAR_CHECKOUT_STARTER,
        "checkout_pro": POLAR_CHECKOUT_PRO,
        "customer_portal": POLAR_CUSTOMER_PORTAL,
    })


@app.route("/profile-links")
def profile_links():
    user = _get_current_user()
    return render_template_string(PROFILE_LINKS_TEMPLATE, user=user, config={
        "checkout_starter": POLAR_CHECKOUT_STARTER,
        "checkout_pro": POLAR_CHECKOUT_PRO,
        "customer_portal": POLAR_CUSTOMER_PORTAL,
    })


# ── Main Template ──────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Instant Transcripts from Any Video</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --red: #B84B3F;
            --green: #709472;
            --grey: #C4C5C7;
            --ink: #0a0a0a;
            --f-wide: 'Michroma', sans-serif;
            --f-tech: 'Space Mono', monospace;
            --radius: 2rem;
            --bw: 1.5px;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:var(--bg); color:var(--ink); font-family:var(--f-tech); line-height:1.4; overflow-x:hidden; }

        .layout { max-width:1100px; margin:0 auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; width:100%; }

        /* ── Nav ── */
        nav {
            display:flex; justify-content:space-between; align-items:center;
            padding:1rem 2rem; background:var(--grey); border-radius:100px;
        }
        .nav-logo { font-family:var(--f-wide); font-size:1.1rem; font-weight:900; }
        .nav-logo em { font-style:normal; font-size:0.5em; vertical-align:super; }
        .nav-links { display:flex; align-items:center; gap:0.5rem; }
        .nav-links a {
            color:var(--ink); text-decoration:none; font-size:0.7rem; font-weight:700;
            text-transform:uppercase; padding:0.5rem 1rem; border-radius:4px;
            border:1px solid transparent; transition:all 0.2s;
        }
        .nav-links a:hover { border-color:var(--ink); background:rgba(0,0,0,0.05); }
        .nav-badge {
            font-size:0.6rem; padding:0.4rem 0.8rem; border-radius:4px;
            font-weight:700; text-transform:uppercase; letter-spacing:0.5px;
        }
        .nav-badge.free { background:rgba(0,0,0,0.08); }
        .nav-badge.starter { background:rgba(66,85,212,0.15); color:#4255d4; }
        .nav-badge.pro { background:rgba(112,148,114,0.3); }

        /* ── Panels ── */
        .panel { border-radius:var(--radius); padding:2rem; position:relative; overflow:hidden; display:flex; flex-direction:column; min-width:0; max-width:100%; box-sizing:border-box; }
        .p-orange { background:var(--orange); }
        .p-red { background:var(--red); }
        .p-green { background:var(--green); }
        .p-grey { background:var(--grey); }

        .label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; opacity:0.6; margin-bottom:0.3rem; display:block; }

        /* ── Hero split ── */
        .hero { display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:1rem; min-height:65vh; max-width:100%; }

        .hero-main { justify-content:space-between; }
        .hero-top { display:flex; justify-content:space-between; border-bottom:var(--bw) solid var(--ink); padding-bottom:1rem; margin-bottom:2rem; }

        .hero-h1 { font-family:var(--f-wide); font-size:clamp(2rem,4.2vw,3.8rem); line-height:0.92; text-transform:uppercase; margin-bottom:1.5rem; letter-spacing:-0.02em; }
        .hero-sub { font-size:0.85rem; max-width:38ch; border-left:2px solid var(--ink); padding-left:1rem; line-height:1.6; }

        /* ── Input machine ── */
        .input-machine { border:var(--bw) solid var(--ink); display:grid; grid-template-columns:1fr auto; margin-top:1rem; }
        .input-machine input {
            background:transparent; border:none; padding:1.3rem 1.5rem;
            font-family:var(--f-tech); font-size:1rem; color:var(--ink); outline:none; width:100%;
        }
        .input-machine input::placeholder { color:rgba(10,10,10,0.35); }
        .input-machine button {
            background:var(--ink); color:var(--orange); border:none; padding:0 2rem;
            font-family:var(--f-wide); font-size:0.7rem; text-transform:uppercase; cursor:pointer; transition:background 0.2s;
        }
        .input-machine button:hover { background:#333; }
        .input-machine button:disabled { opacity:0.4; cursor:not-allowed; }
        .input-machine button.loading { color:transparent; position:relative; }
        .input-machine button.loading::after {
            content:''; position:absolute; width:16px; height:16px;
            border:2px solid rgba(240,168,96,0.3); border-top-color:var(--orange);
            border-radius:50%; top:50%; left:50%; margin:-8px 0 0 -8px;
            animation:spin 0.5s linear infinite;
        }
        @keyframes spin { to { transform:rotate(360deg); } }

        .barcode {
            height:16px; width:80px; display:inline-block;
            background:repeating-linear-gradient(90deg, var(--ink), var(--ink) 2px, transparent 2px, transparent 4px);
            opacity:0.4;
            position:relative;
        }
        .barcode::after {
            content:'';
            position:absolute;
            right:0; top:0;
            width:2px; height:100%;
            background:var(--ink);
            animation:barBlink 1s ease-in-out infinite;
        }
        @keyframes barBlink { 0%,100%{opacity:1} 50%{opacity:0} }
        .input-footer { margin-top:1rem; display:flex; gap:1rem; align-items:center; }

        /* ── Controls row ── */
        .controls { display:flex; align-items:center; justify-content:space-between; margin-top:0.8rem; flex-wrap:wrap; gap:0.5rem; }
        .controls select {
            background:transparent; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:0.4rem 0.6rem; font-family:var(--f-tech); font-size:0.65rem;
        }
        .toggle-wrap {
            display:flex; align-items:center; gap:6px; font-size:0.65rem;
            text-transform:uppercase; letter-spacing:0.05em; cursor:pointer; opacity:0.7;
        }
        .toggle-wrap input { display:none; }
        .toggle-track { width:28px; height:16px; background:rgba(0,0,0,0.2); border-radius:8px; position:relative; transition:0.2s; }
        .toggle-track::after { content:''; width:12px; height:12px; background:var(--ink); border-radius:50%; position:absolute; top:2px; left:2px; transition:0.2s; opacity:0.5; }
        .toggle-wrap input:checked + .toggle-track { background:rgba(0,0,0,0.4); }
        .toggle-wrap input:checked + .toggle-track::after { left:14px; opacity:1; }

        .batch-area { display:none; margin-top:0.8rem; }
        .batch-area.open { display:block; }
        .batch-area textarea {
            width:100%; min-height:80px; background:transparent; border:var(--bw) solid var(--ink);
            padding:1rem; font-family:var(--f-tech); font-size:0.75rem; color:var(--ink); resize:vertical; outline:none;
        }
        .batch-area textarea::placeholder { color:rgba(10,10,10,0.3); }

        /* ── Side panels ── */
        .hero-side { display:flex; flex-direction:column; gap:1rem; }

        .stat-block { flex-grow:1; }
        .stat-block h2 { font-family:var(--f-wide); font-size:1.4rem; text-transform:uppercase; }
        .meter-box { border:var(--bw) solid var(--ink); padding:0.8rem 1rem; margin-top:0.8rem; display:flex; justify-content:space-between; align-items:center; min-width:0; }
        .digital { font-size:1rem; font-weight:700; border:var(--bw) solid var(--ink); padding:0.2rem 0.6rem; background:rgba(255,255,255,0.1); }

        .ticker-wrap { overflow:hidden; border-top:var(--bw) solid var(--ink); padding-top:1rem; margin-top:auto; }
        .ticker-items { display:flex; gap:6px; animation:scroll 25s linear infinite; width:max-content; }
        .ticker-items:hover { animation-play-state:paused; }
        @keyframes scroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
        .ticker-item {
            padding:4px 10px; border:var(--bw) solid var(--ink); font-size:0.55rem;
            font-weight:700; text-transform:uppercase; white-space:nowrap; letter-spacing:0.03em;
            display:inline-flex; align-items:center; gap:5px;
        }
        .ticker-item svg { width:12px; height:12px; fill:var(--ink); flex-shrink:0; }

        .blink { animation:blinker 2s linear infinite; }
        @keyframes blinker { 50%{opacity:0} }

        /* ── Status bar ── */
        .status-bar { display:none; }
        .status-bar.on {
            display:flex; align-items:center; gap:12px;
            background:var(--grey); border-radius:var(--radius); padding:1rem 2rem;
        }
        .status-dot { width:6px; height:6px; border-radius:50%; background:var(--ink); animation:blinker 1s ease infinite; }
        .prog-track { flex:1; height:3px; background:rgba(0,0,0,0.15); }
        .prog-bar { height:100%; background:var(--ink); transition:width 0.4s; width:0; }

        /* ── Export bar ── */
        .export-bar { display:none; gap:8px; justify-content:center; }
        .export-bar.on { display:flex; }
        .export-btn {
            background:var(--grey); border:none; color:var(--ink); padding:0.6rem 1.2rem;
            border-radius:4px; font-family:var(--f-tech); font-size:0.65rem; cursor:pointer;
            text-transform:uppercase; letter-spacing:0.05em; transition:0.2s;
        }
        .export-btn:hover { background:var(--orange); }

        /* ── Result cards ── */
        .result-card {
            background:var(--grey); border-radius:var(--radius); padding:2rem;
            animation:cardUp 0.4s ease;
        }
        .result-card + .result-card { margin-top:1rem; }
        .result-card.err { border-left:4px solid var(--red); }
        @keyframes cardUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }

        .result-url { font-size:0.6rem; opacity:0.5; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-bottom:1rem; }
        .result-url a { color:var(--ink); text-decoration:none; }

        .spec-grid { display:grid; border:var(--bw) solid var(--ink); background:var(--ink); gap:var(--bw); margin-bottom:1.2rem; }
        .spec-grid.cols-4 { grid-template-columns:repeat(4,1fr); }
        .spec-cell { background:var(--grey); padding:1rem; text-align:center; }
        .spec-val { font-size:1.1rem; font-weight:700; }
        .spec-lbl { font-size:0.5rem; text-transform:uppercase; letter-spacing:1px; opacity:0.5; margin-top:4px; }

        .transcript-box { border:var(--bw) solid var(--ink); padding:1.2rem; }
        .transcript-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; }
        .copy-btn {
            background:none; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:3px 10px; font-size:0.55rem; cursor:pointer; font-family:var(--f-tech);
            text-transform:uppercase; transition:0.2s;
        }
        .copy-btn:hover { background:var(--ink); color:var(--orange); }
        .copy-btn.ok { background:var(--green); color:#fff; border-color:var(--green); }
        .transcript-text { font-size:0.82rem; line-height:1.7; opacity:0.8; }

        /* ── Auth modal ── */
        .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); z-index:100; justify-content:center; align-items:center; }
        .modal-overlay.open { display:flex; }
        .modal-box { background:var(--grey); border-radius:var(--radius); padding:2rem; width:90%; max-width:380px; text-align:center; }
        .modal-title { font-family:var(--f-wide); font-size:0.9rem; text-transform:uppercase; margin-bottom:4px; }
        .modal-sub { font-size:0.75rem; opacity:0.6; }
        .modal-input {
            width:100%; margin-top:1rem; background:transparent; border:var(--bw) solid var(--ink);
            padding:1rem; font-family:var(--f-tech); font-size:0.85rem; color:var(--ink); outline:none;
        }
        .modal-input::placeholder { color:rgba(10,10,10,0.35); }
        .modal-btn {
            width:100%; margin-top:0.8rem; background:var(--ink); color:var(--orange); border:none;
            padding:1rem; font-family:var(--f-wide); font-size:0.7rem; text-transform:uppercase; cursor:pointer;
        }
        .modal-btn:disabled { opacity:0.4; cursor:not-allowed; }
        .modal-err { color:var(--red); font-size:0.7rem; margin-top:0.5rem; min-height:1.2em; }
        .auth-tab {
            flex:1; background:transparent; border:var(--bw) solid var(--ink); padding:0.7rem;
            font-family:var(--f-wide); font-size:0.6rem; text-transform:uppercase; cursor:pointer;
            color:var(--ink); opacity:0.4; transition:all 0.2s;
        }
        .auth-tab.active { opacity:1; background:var(--ink); color:var(--orange); }

        /* ── Footer ── */
        .tech-footer {
            border:1px solid #333; color:#555; padding:1.5rem 2rem; font-size:0.6rem;
            text-transform:uppercase; display:flex; justify-content:space-between; letter-spacing:0.05em;
        }
        .tech-footer a { color:#555; text-decoration:none; }
        .tech-footer a:hover { color:var(--orange); }

        @media (max-width:800px) {
            .layout { padding:0.5rem; gap:0.5rem; overflow:hidden; }
            .hero { grid-template-columns:minmax(0,1fr); min-height:auto; gap:0.5rem; overflow:hidden; }
            .hero-h1 { font-size:clamp(1.6rem,7vw,2.2rem); letter-spacing:-0.03em; word-break:break-word; }
            nav { padding:0.6rem 1rem; border-radius:60px; gap:0.3rem; }
            .nav-logo { font-size:0.85rem; }
            .nav-links { gap:0.2rem; }
            .nav-links a { font-size:0.55rem; padding:0.35rem 0.5rem; }
            .nav-badge { font-size:0.5rem; padding:0.3rem 0.5rem; }
            .panel { padding:1rem; border-radius:1rem; }
            .hero-main { padding:1rem; }
            .hero-top { flex-direction:column; gap:0.2rem; padding-bottom:0.5rem; margin-bottom:0.6rem; }
            .hero-sub { font-size:0.78rem; line-height:1.6; padding-left:0.8rem; }
            .label { font-size:0.6rem; }
            .input-machine { grid-template-columns:1fr; }
            .input-machine input { padding:1rem; font-size:0.85rem; }
            .input-machine button { padding:0.9rem 1.5rem; font-size:0.65rem; }
            .controls { margin-top:0.5rem; }
            .controls select { font-size:0.7rem; padding:0.4rem 0.6rem; }
            .stat-block { padding:1rem; }
            .stat-block h2 { font-size:1.1rem; }
            .stat-block p { font-size:0.78rem; }
            .meter-box { padding:0.6rem 0.8rem; }
            .digital { font-size:0.75rem; padding:0.15rem 0.5rem; }
            .ticker-item { font-size:0.5rem; padding:3px 8px; }
            .ticker-wrap { padding-top:0.5rem; }
            .hero-side { gap:0.5rem; }
            .spec-grid.cols-4 { grid-template-columns:repeat(2,1fr); }
            .input-footer { font-size:0.6rem; margin-top:0.5rem; }
            .barcode { height:10px; width:50px; }
            .tech-footer {
                flex-direction:column; gap:0.5rem; padding:1.2rem;
                font-size:0.6rem; text-align:center;
            }
            .tech-footer div { text-align:center !important; }
            .modal-box { padding:1.5rem; border-radius:1rem; width:95%; }
            .result-card { padding:1rem; border-radius:1rem; }
            .export-btn { padding:0.5rem 0.8rem; font-size:0.6rem; }
            .status-bar.on { padding:0.8rem 1rem; border-radius:1rem; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <!-- Nav -->
        <nav>
            <div class="nav-logo">TRANSCRIPTX<em>®</em></div>
            <div class="nav-links">
                {% if user.logged_in %}
                <span class="nav-badge {{ user.plan }}">{{ user.plan_name }} — {{ user.credits_label }}</span>
                {% if user.plan != 'free' %}
                <a href="{{ config.customer_portal }}">Billing</a>
                {% else %}
                <a href="/pricing">Upgrade</a>
                {% endif %}
                <a href="/profile-links">Links</a>
                <a href="#" onclick="logout();return false">Logout</a>
                {% else %}
                <a href="/profile-links">Links</a>
                <a href="#" onclick="showAuth('login');return false">Login</a>
                <a href="#" onclick="showAuth('signup');return false">Sign Up</a>
                {% endif %}
            </div>
        </nav>

        <!-- Hero -->
        <div class="hero">
            <div class="panel p-orange hero-main">
                <div class="hero-top">
                    <span class="label">System Status: Online</span>
                    <span class="label">TX-{{ user.credits_label }} remaining</span>
                </div>

                <div>
                    <h1 class="hero-h1">Instant<br>Transcripts</h1>
                    <div class="hero-sub">
                        Paste any video link. Get a perfect transcript in seconds. YouTube, TikTok, Instagram, X — 1000+ platforms.
                    </div>
                </div>

                <div style="margin-top:auto; padding-top:2rem;">
                    <span class="label">Initialize Transcription</span>
                    <div class="input-machine">
                        <input type="text" id="urlInput" placeholder="PASTE_VIDEO_URL" onkeydown="if(event.key==='Enter')go()">
                        <button id="goBtn" onclick="go()">EXTRACT ➔</button>
                    </div>
                    <div class="controls">
                        <label class="toggle-wrap" {% if not user.batch %}style="opacity:0.3;pointer-events:none"{% endif %}>
                            <input type="checkbox" id="batchToggle" onchange="toggleBatch()">
                            <div class="toggle-track"></div>
                            Batch {% if not user.batch %}(paid){% endif %}
                        </label>
                        <select id="modelSel">
                            <option value="whisper-large-v3-turbo">TURBO (FAST)</option>
                            <option value="whisper-large-v3">LARGE-V3 (BEST)</option>
                        </select>
                    </div>
                    <div class="batch-area" id="batchArea">
                        <textarea id="batchUrls" placeholder="One URL per line..."></textarea>
                    </div>
                    <div class="input-footer">
                        <div class="barcode"></div>
                        <span class="label" style="margin:0">Transcription Engine</span>
                    </div>
                </div>
            </div>

            <div class="hero-side">
                <div class="panel p-grey stat-block">
                    <span class="label">Supported Platforms</span>
                    <h2>1000+</h2>
                    <p style="font-size:0.75rem; opacity:0.7; margin-top:0.3rem;">Any public video URL</p>
                    <div class="meter-box">
                        <span class="label" style="margin:0">Engine</span>
                        <span class="digital">AI</span>
                    </div>
                    <div class="meter-box" style="margin-top:4px;">
                        <span class="label" style="margin:0">Accuracy</span>
                        <span class="digital">99.2%</span>
                    </div>
                    <div class="ticker-wrap">
                        <div class="ticker-items">
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>YouTube</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>TikTok</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"/></svg>Instagram</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"/></svg>X</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg>Facebook</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>LinkedIn</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"/></svg>Reddit</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M23.9765 6.4168c-.105 2.338-1.739 5.5429-4.894 9.6088-3.2679 4.247-6.0258 6.3699-8.2898 6.3699-1.409 0-2.578-1.294-3.553-3.881l-1.9179-7.1138c-.719-2.584-1.488-3.878-2.312-3.878-.179 0-.806.378-1.8809 1.132l-1.129-1.457a315.06 315.06 0 003.501-3.1279c1.579-1.368 2.765-2.085 3.5539-2.159 1.867-.18 3.016 1.1 3.447 3.838.465 2.953.789 4.789.971 5.5069.5389 2.45 1.1309 3.674 1.7759 3.674.502 0 1.256-.796 2.265-2.385 1.004-1.589 1.54-2.797 1.612-3.628.144-1.371-.395-2.061-1.614-2.061-.574 0-1.167.121-1.777.391 1.186-3.8679 3.434-5.7568 6.7619-5.6368 2.4729.06 3.6279 1.664 3.4929 4.7969z"/></svg>Vimeo</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z"/></svg>Twitch</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M14.4528 13.5458c.8064-.6542.9297-1.8381.2756-2.6445a1.8802 1.8802 0 0 0-.2756-.2756 21.2127 21.2127 0 0 0-4.3121-2.776c-1.066-.51-2.256.2-2.4261 1.414a23.5226 23.5226 0 0 0-.14 5.5021c.116 1.23 1.292 1.964 2.372 1.492a19.6285 19.6285 0 0 0 4.5062-2.704v-.008zm6.9322-5.4002c2.0335 2.228 2.0396 5.637.014 7.8723A26.1487 26.1487 0 0 1 8.2946 23.846c-2.6848.6713-5.4168-.914-6.1662-3.5781-1.524-5.2002-1.3-11.0803.17-16.3045.772-2.744 3.3521-4.4661 6.0102-3.832 4.9242 1.174 9.5443 4.196 13.0764 8.0121v.002z"/></svg>Rumble</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285 1.33-3.082.88-.76 2.119-1.207 3.583-1.291a13.853 13.853 0 0 1 3.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844 0-1.992.232-2.721 1.32L7.734 7.847c.98-1.454 2.568-2.256 4.478-2.256h.044c3.194.02 5.097 1.975 5.287 5.388.108.046.216.094.321.142 1.49.7 2.58 1.761 3.154 3.07.797 1.82.871 4.79-1.548 7.158-1.85 1.81-4.094 2.628-7.277 2.65Zm1.003-11.69c-.242 0-.487.007-.739.021-1.836.103-2.98.946-2.916 2.143.067 1.256 1.452 1.839 2.784 1.767 1.224-.065 2.818-.543 3.086-3.71a10.5 10.5 0 0 0-2.215-.221z"/></svg>Threads</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M23.999 14.165c-.052 1.796-1.612 3.169-3.4 3.169h-8.18a.68.68 0 0 1-.675-.683V7.862a.747.747 0 0 1 .452-.724s.75-.513 2.333-.513a5.364 5.364 0 0 1 2.763.755 5.433 5.433 0 0 1 2.57 3.54c.282-.08.574-.121.868-.12.884 0 1.73.358 2.347.992s.948 1.49.922 2.373ZM10.721 8.421c.247 2.98.427 5.697 0 8.672a.264.264 0 0 1-.53 0c-.395-2.946-.22-5.718 0-8.672a.264.264 0 0 1 .53 0ZM9.072 9.448c.285 2.659.37 4.986-.006 7.655a.277.277 0 0 1-.55 0c-.331-2.63-.256-5.02 0-7.655a.277.277 0 0 1 .556 0Zm-1.663-.257c.27 2.726.39 5.171 0 7.904a.266.266 0 0 1-.532 0c-.38-2.69-.257-5.21 0-7.904a.266.266 0 0 1 .532 0Zm-1.647.77a26.108 26.108 0 0 1-.008 7.147.272.272 0 0 1-.542 0 27.955 27.955 0 0 1 0-7.147.275.275 0 0 1 .55 0Zm-1.67 1.769c.421 1.865.228 3.5-.029 5.388a.257.257 0 0 1-.514 0c-.21-1.858-.398-3.549 0-5.389a.272.272 0 0 1 .543 0Zm-1.655-.273c.388 1.897.26 3.508-.01 5.412-.026.28-.514.283-.54 0-.244-1.878-.347-3.54-.01-5.412a.283.283 0 0 1 .56 0Zm-1.668.911c.4 1.268.257 2.292-.026 3.572a.257.257 0 0 1-.514 0c-.241-1.262-.354-2.312-.023-3.572a.283.283 0 0 1 .563 0Z"/></svg>SoundCloud</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.151.929.4.267.249.391.551.391.907 0 .355-.124.657-.373.906zM5.333 7.24c-.746.018-1.373.276-1.88.773-.506.498-.769 1.13-.786 1.894v7.52c.017.764.28 1.395.786 1.893.507.498 1.134.756 1.88.773h13.334c.746-.017 1.373-.275 1.88-.773.506-.498.769-1.129.786-1.893v-7.52c-.017-.765-.28-1.396-.786-1.894-.507-.497-1.134-.755-1.88-.773zM8 11.107c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c0-.373.129-.689.386-.947.258-.257.574-.386.947-.386zm8 0c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373Z"/></svg>Bilibili</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12 1.033-.301.165-.088.344-.104.464-.104.182 0 .359.029.509.09.45.149.734.479.734.838.015.449-.39.839-1.213 1.168-.089.029-.209.075-.344.119-.45.135-1.139.36-1.333.81-.09.224-.061.524.12.868l.015.015c.06.136 1.526 3.475 4.791 4.014.255.044.435.27.42.509 0 .075-.015.149-.045.225-.24.569-1.273.988-3.146 1.271-.059.091-.12.375-.164.57-.029.179-.074.36-.134.553-.076.271-.27.405-.555.405h-.03c-.135 0-.313-.031-.538-.074-.36-.075-.765-.135-1.273-.135-.3 0-.599.015-.913.074-.6.104-1.123.464-1.723.884-.853.599-1.826 1.288-3.294 1.288-.06 0-.119-.015-.18-.015h-.149c-1.468 0-2.427-.675-3.279-1.288-.599-.42-1.107-.779-1.707-.884-.314-.045-.629-.074-.928-.074-.54 0-.958.089-1.272.149-.211.043-.391.074-.54.074-.374 0-.523-.224-.583-.42-.061-.192-.09-.389-.135-.567-.046-.181-.105-.494-.166-.57-1.918-.222-2.95-.642-3.189-1.226-.031-.063-.052-.15-.055-.225-.015-.243.165-.465.42-.509 3.264-.54 4.73-3.879 4.791-4.02l.016-.029c.18-.345.224-.645.119-.869-.195-.434-.884-.658-1.332-.809-.121-.029-.24-.074-.346-.119-1.107-.435-1.257-.93-1.197-1.273.09-.479.674-.793 1.168-.793.146 0 .27.029.383.074.42.194.789.3 1.104.3.234 0 .384-.06.465-.105l-.046-.569c-.098-1.626-.225-3.651.307-4.837C7.392 1.077 10.739.807 11.727.807l.419-.015h.06z"/></svg>Snapchat</span>
                            <span class="ticker-item">1000+ more</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>YouTube</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>TikTok</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"/></svg>Instagram</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"/></svg>X</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg>Facebook</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>LinkedIn</span>
                            <span class="ticker-item"><svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"/></svg>Reddit</span>
                            <span class="ticker-item">1000+ more</span>
                        </div>
                    </div>
                </div>
                <div class="panel p-red" style="justify-content:center; align-items:center; text-align:center; padding:1.5rem;">
                    <span class="label">Transcription Engine</span>
                    <h3 class="blink" style="font-family:var(--f-wide); text-transform:uppercase;">READY</h3>
                </div>
            </div>
        </div>

        <!-- Status -->
        <div class="status-bar" id="status">
            <div class="status-dot"></div>
            <span id="statusMsg" style="font-size:0.75rem;">Processing...</span>
            <div class="prog-track"><div class="prog-bar" id="prog"></div></div>
        </div>

        <!-- Export -->
        <div class="export-bar" id="exportBar">
            <button class="export-btn" onclick="expCSV()">Export CSV</button>
            <button class="export-btn" onclick="expJSON()">Export JSON</button>
            <button class="export-btn" onclick="clearAll()">Clear</button>
        </div>

        <!-- Results -->
        <div id="results"></div>

        <!-- Auth modal -->
        <div class="modal-overlay" id="authModal" onclick="if(event.target===this)hideAuth()">
            <div class="modal-box">
                <!-- Tab toggle -->
                <div id="authTabs" style="display:flex;gap:0;margin-bottom:1.2rem;">
                    <button class="auth-tab active" id="tabLogin" onclick="switchTab('login')">LOG IN</button>
                    <button class="auth-tab" id="tabSignup" onclick="switchTab('signup')">SIGN UP</button>
                </div>

                <!-- Login form -->
                <div id="loginForm">
                    <input type="email" class="modal-input" id="loginEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="loginPassword" placeholder="Password" autocomplete="current-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doLogin()">
                    <div class="modal-err" id="loginErr"></div>
                    <button class="modal-btn" onclick="doLogin()">LOG IN ➔</button>
                </div>

                <!-- Signup form -->
                <div id="signupForm" style="display:none;">
                    <input type="email" class="modal-input" id="signupEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="signupPassword" placeholder="Password (6+ chars)" autocomplete="new-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doSignup()">
                    <div class="modal-err" id="signupErr"></div>
                    <button class="modal-btn" onclick="doSignup()">SIGN UP ➔</button>
                </div>

                <!-- Verify form -->
                <div id="verifyForm" style="display:none;">
                    <div class="modal-title">Check Your Email</div>
                    <div class="modal-sub" id="verifySub">Enter the 6-digit code we sent</div>
                    <input type="text" class="modal-input" id="verifyCode" placeholder="000000" maxlength="6" style="text-align:center;font-size:1.5rem;letter-spacing:0.4em;" onkeydown="if(event.key==='Enter')doVerify()">
                    <div class="modal-err" id="verifyErr"></div>
                    <button class="modal-btn" onclick="doVerify()">VERIFY ➔</button>
                    <div style="margin-top:0.8rem;text-align:center;">
                        <a href="#" onclick="resendCode();return false" style="font-size:0.7rem;color:var(--ink);opacity:0.5;">Resend code</a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="tech-footer">
            <div>TranscriptX Systems</div>
            <div style="text-align:right;">Built by <a href="https://google.com">x362 IIC</a><br>1000+ platforms supported</div>
        </footer>
    </div>

    <script>
        let all = [];

        function toggleBatch() {
            document.getElementById('batchArea').classList.toggle('open', document.getElementById('batchToggle').checked);
        }

        function getUrls() {
            if (document.getElementById('batchToggle').checked) {
                return document.getElementById('batchUrls').value.split('\\n').map(u=>u.trim()).filter(u=>u.startsWith('http'));
            }
            const u = document.getElementById('urlInput').value.trim();
            return u ? [u] : [];
        }

        async function go() {
            {% if not user.logged_in %}
            showAuth('signup');
            return;
            {% endif %}

            const urls = getUrls();
            if (!urls.length) return;

            const btn = document.getElementById('goBtn');
            const status = document.getElementById('status');
            const msg = document.getElementById('statusMsg');
            const prog = document.getElementById('prog');
            const model = document.getElementById('modelSel').value;

            btn.disabled = true;
            btn.classList.add('loading');
            status.classList.add('on');

            var fakeTimer = null;
            function startFakeProgress(base, span) {
                var start = Date.now(), dur = 70000;
                prog.style.transition = 'none';
                prog.style.width = base + '%';
                fakeTimer = setInterval(function() {
                    var t = Math.min((Date.now() - start) / dur, 1);
                    var ease = 1 - Math.pow(1 - t, 3);
                    prog.style.width = (base + ease * span * 0.9) + '%';
                }, 200);
            }
            function stopFakeProgress(pct) {
                clearInterval(fakeTimer);
                return new Promise(function(resolve) {
                    requestAnimationFrame(function() {
                        prog.style.transition = 'width 0.4s ease-out';
                        prog.style.width = pct + '%';
                        setTimeout(resolve, 450);
                    });
                });
            }

            for (let i = 0; i < urls.length; i++) {
                msg.textContent = urls.length > 1 ? `Processing ${i+1}/${urls.length}...` : 'Transcribing...';
                var base = (i / urls.length) * 100;
                var span = 100 / urls.length;
                startFakeProgress(base, span);

                var result = null, isErr = false;
                try {
                    const r = await fetch('/api/extract', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({url: urls[i], model})
                    });
                    const d = await r.json();

                    if (r.status === 403) {
                        showUpgrade(d.error);
                        await stopFakeProgress(((i + 1) / urls.length) * 100);
                        break;
                    }
                    result = d;
                } catch(e) {
                    result = {url:urls[i], status:'error', error:e.message};
                    isErr = true;
                }

                await stopFakeProgress(((i + 1) / urls.length) * 100);
                all.push(result);
                render(result);
                updateCredits();
            }

            btn.disabled = false;
            btn.classList.remove('loading');
            status.classList.remove('on');
            prog.style.transition = 'none';
            prog.style.width = '0%';
            if (all.length) document.getElementById('exportBar').classList.add('on');
            document.getElementById('urlInput').value = '';
            document.getElementById('batchUrls').value = '';
        }

        function showUpgrade(msg) {
            document.getElementById('results').insertAdjacentHTML('afterbegin', `
                <div class="result-card" style="text-align:center;border-left:4px solid var(--orange);">
                    <div style="font-family:var(--f-wide);font-size:0.9rem;text-transform:uppercase;margin-bottom:8px;">${msg}</div>
                    <a href="/pricing" style="color:var(--ink);">View Plans →</a>
                </div>
            `);
        }

        async function updateCredits() {
            try {
                const r = await fetch('/api/me');
                const u = await r.json();
                document.querySelector('.nav-badge').textContent = `${u.plan_name} — ${u.credits_label}`;
                document.querySelector('.nav-badge').className = `nav-badge ${u.plan}`;
            } catch(e) {}
        }

        function fmt(n) {
            if (!n) return '0';
            if (n>=1e6) return (n/1e6).toFixed(1)+'M';
            if (n>=1e3) return (n/1e3).toFixed(1)+'K';
            return n.toLocaleString();
        }

        function render(d) {
            const c = document.getElementById('results');
            if (d.status === 'error') {
                c.insertAdjacentHTML('afterbegin', `
                    <div class="result-card err">
                        <div class="result-url"><a href="${d.url}" target="_blank">${d.url}</a></div>
                        <div style="color:var(--red);font-size:0.85rem;">${d.error||'Unknown error'}</div>
                    </div>`);
                return;
            }
            const id = 'tx-'+Date.now();
            c.insertAdjacentHTML('afterbegin', `
                <div class="result-card">
                    <div class="result-url"><a href="${d.url}" target="_blank">${d.url}</a></div>
                    <div class="spec-grid cols-4">
                        <div class="spec-cell"><div class="spec-val">${fmt(d.views)}</div><div class="spec-lbl">Views</div></div>
                        <div class="spec-cell"><div class="spec-val">${fmt(d.likes)}</div><div class="spec-lbl">Likes</div></div>
                        <div class="spec-cell"><div class="spec-val">${fmt(d.comments)}</div><div class="spec-lbl">Comments</div></div>
                        <div class="spec-cell"><div class="spec-val">${d.duration_formatted||'N/A'}</div><div class="spec-lbl">Duration</div></div>
                    </div>
                    <div class="transcript-box">
                        <div class="transcript-head">
                            <span class="label" style="margin:0">${d.language||'auto'}</span>
                            <button class="copy-btn" onclick="clip(this,'${id}')">COPY</button>
                        </div>
                        <div class="transcript-text" id="${id}">${d.transcript||'No transcript'}</div>
                    </div>
                </div>`);
        }

        function clip(btn, id) {
            navigator.clipboard.writeText(document.getElementById(id).innerText);
            btn.textContent='COPIED'; btn.classList.add('ok');
            setTimeout(()=>{btn.textContent='COPY';btn.classList.remove('ok');},1500);
        }

        function expCSV() {
            const ok=all.filter(r=>r.status==='success');
            if(!ok.length) return;
            let csv='URL,Views,Likes,Comments,Duration,Language,Transcript\\n';
            ok.forEach(r=>{csv+=`"${r.url}",${r.views||0},${r.likes||0},${r.comments||0},"${r.duration_formatted||''}","${r.language||''}","${(r.transcript||'').replace(/"/g,'""')}"\\n`;});
            dl('transcripts.csv',csv,'text/csv');
        }
        function expJSON(){dl('transcripts.json',JSON.stringify(all,null,2),'application/json');}
        function dl(n,c,t){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([c],{type:t}));a.download=n;a.click();}
        function clearAll(){all=[];document.getElementById('results').innerHTML='';document.getElementById('exportBar').classList.remove('on');}

        let authEmail = '';

        function showAuth(tab) {
            document.getElementById('authModal').classList.add('open');
            switchTab(tab || 'login');
        }
        function hideAuth() {
            document.getElementById('authModal').classList.remove('open');
            document.getElementById('loginErr').textContent = '';
            document.getElementById('signupErr').textContent = '';
            document.getElementById('verifyErr').textContent = '';
        }
        function switchTab(tab) {
            var le = document.getElementById('loginEmail'), se = document.getElementById('signupEmail');
            if (tab === 'signup') se.value = le.value;
            if (tab === 'login') le.value = se.value;
            document.getElementById('loginForm').style.display = tab === 'login' ? '' : 'none';
            document.getElementById('signupForm').style.display = tab === 'signup' ? '' : 'none';
            document.getElementById('verifyForm').style.display = tab === 'verify' ? '' : 'none';
            document.getElementById('authTabs').style.display = tab === 'verify' ? 'none' : 'flex';
            document.getElementById('tabLogin').classList.toggle('active', tab === 'login');
            document.getElementById('tabSignup').classList.toggle('active', tab === 'signup');
            if (tab === 'login') le.focus();
            if (tab === 'signup') se.focus();
            if (tab === 'verify') document.getElementById('verifyCode').focus();
        }

        async function doSignup() {
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const err = document.getElementById('signupErr');
            err.textContent = '';
            if (!email) { err.textContent = 'Enter your email'; return; }
            if (password.length < 6) { err.textContent = 'Password must be 6+ characters'; return; }
            try {
                const r = await fetch('/api/signup', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email, password})
                });
                const d = await r.json();
                if (d.step === 'verify') {
                    authEmail = email;
                    document.getElementById('verifySub').textContent = 'Code sent to ' + email;
                    switchTab('verify');
                } else {
                    err.textContent = d.error || 'Something went wrong';
                }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }

        async function doVerify() {
            const code = document.getElementById('verifyCode').value.trim();
            const err = document.getElementById('verifyErr');
            err.textContent = '';
            if (code.length !== 6) { err.textContent = 'Enter the 6-digit code'; return; }
            try {
                const r = await fetch('/api/verify', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email: authEmail, code})
                });
                const d = await r.json();
                if (r.ok) { location.reload(); }
                else { err.textContent = d.error || 'Invalid code'; }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }

        async function resendCode() {
            if (!authEmail) return;
            try {
                await fetch('/api/resend-code', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email: authEmail})
                });
                document.getElementById('verifyErr').textContent = '';
                document.getElementById('verifySub').textContent = 'New code sent to ' + authEmail;
            } catch(e) {}
        }

        async function doLogin() {
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;
            const err = document.getElementById('loginErr');
            err.textContent = '';
            if (!email) { err.textContent = 'Enter your email'; return; }
            if (!password) { err.textContent = 'Enter your password'; return; }
            try {
                const r = await fetch('/api/login', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email, password})
                });
                const d = await r.json();
                if (d.status === 'ok') { location.reload(); }
                else if (d.status === 'verify') {
                    authEmail = email;
                    document.getElementById('verifySub').textContent = 'Code sent to ' + email;
                    switchTab('verify');
                }
                else { err.textContent = d.error || 'Login failed'; }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }

        async function logout() {
            await fetch('/api/logout', {method:'POST'});
            location.reload();
        }

    </script>
</body>
</html>
"""


# ── Pricing Template ───────────────────────────────────────

PRICING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Pricing</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --red: #B84B3F;
            --green: #709472;
            --grey: #C4C5C7;
            --ink: #0a0a0a;
            --f-wide: 'Michroma', sans-serif;
            --f-tech: 'Space Mono', monospace;
            --radius: 2rem;
            --bw: 1.5px;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:var(--bg); color:var(--ink); font-family:var(--f-tech); line-height:1.4; }

        .layout { max-width:1100px; margin:0 auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; }

        nav {
            display:flex; justify-content:space-between; align-items:center;
            padding:1rem 2rem; background:var(--grey); border-radius:100px;
        }
        .nav-logo { font-family:var(--f-wide); font-size:1.1rem; font-weight:900; text-decoration:none; color:var(--ink); }
        .nav-logo em { font-style:normal; font-size:0.5em; vertical-align:super; }
        nav a.back { font-size:0.7rem; font-weight:700; text-transform:uppercase; color:var(--ink); text-decoration:none; border:1px solid transparent; padding:0.5rem 1rem; border-radius:4px; }
        nav a.back:hover { border-color:var(--ink); }

        .panel { border-radius:var(--radius); padding:2rem; position:relative; overflow:hidden; display:flex; flex-direction:column; }
        .p-orange { background:var(--orange); }
        .p-green { background:var(--green); }
        .p-grey { background:var(--grey); }

        .label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; opacity:0.6; margin-bottom:0.3rem; display:block; }

        .pricing-head { text-align:center; color:var(--grey); padding:3rem 0 1rem; }
        .pricing-head h1 { font-family:var(--f-wide); font-size:clamp(1.5rem,3vw,2.5rem); text-transform:uppercase; }
        .pricing-head p { font-size:0.8rem; opacity:0.6; margin-top:0.5rem; }

        .plans { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }

        .plan-name { font-family:var(--f-wide); font-size:0.85rem; text-transform:uppercase; margin-bottom:0.5rem; }
        .plan-price { font-size:2.2rem; font-weight:700; font-family:var(--f-wide); }
        .plan-price span { font-size:0.8rem; font-weight:400; }
        .plan-features { list-style:none; margin:1.5rem 0; font-size:0.75rem; line-height:2.2; }
        .plan-features li::before { content:'→ '; opacity:0.5; }

        .plan-btn {
            display:block; width:100%; padding:1rem; text-align:center;
            font-family:var(--f-wide); font-size:0.7rem; text-transform:uppercase;
            text-decoration:none; cursor:pointer; border:none; transition:0.2s;
        }
        .plan-btn.dark { background:var(--ink); color:var(--orange); }
        .plan-btn.dark:hover { background:#333; }
        .plan-btn.outline { background:transparent; border:var(--bw) solid var(--ink); color:var(--ink); }
        .plan-btn.green { background:var(--ink); color:var(--green); }
        .plan-btn.green:hover { background:#333; }

        .spec-grid { display:grid; border:var(--bw) solid var(--ink); background:var(--ink); gap:var(--bw); margin-top:1rem; }
        .spec-grid.cols-2 { grid-template-columns:1fr 1fr; }
        .spec-cell { padding:1rem; text-align:center; }
        .p-orange .spec-cell { background:var(--orange); }
        .p-green .spec-cell { background:var(--green); }
        .p-grey .spec-cell { background:var(--grey); }

        .tech-footer {
            border:1px solid #333; color:#555; padding:1.5rem 2rem; font-size:0.6rem;
            text-transform:uppercase; display:flex; justify-content:space-between;
        }

        @media (max-width:800px) {
            .plans { grid-template-columns:1fr; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <nav>
            <a class="nav-logo" href="/">TRANSCRIPTX<em>®</em></a>
            <div style="display:flex;gap:0.5rem;">
                <a class="back" href="/profile-links">Links</a>
                <a class="back" href="/">← Back</a>
            </div>
        </nav>

        <div class="pricing-head">
            <h1>Simple Pricing</h1>
            <p>Instagram, TikTok, YouTube, X, and 1000+ more. Start free.</p>
        </div>

        <div class="plans">
            <div class="panel p-grey">
                <span class="label">Free Tier</span>
                <div class="plan-name">Free</div>
                <div class="plan-price">$0</div>
                <ul class="plan-features">
                    <li>3 transcripts / month</li>
                    <li>Any platform, any video</li>
                    <li>AI-powered transcription</li>
                    <li>Copy to clipboard</li>
                </ul>
                <div class="plan-btn outline" style="cursor:default; margin-top:auto;">Current</div>
            </div>

            <div class="panel p-orange">
                <span class="label">Most Popular</span>
                <div class="plan-name">Starter</div>
                <div class="plan-price">$2<span>/mo</span></div>
                <ul class="plan-features">
                    <li>50 transcripts / month</li>
                    <li>All 1000+ platforms</li>
                    <li>Batch mode</li>
                    <li>CSV + JSON export</li>
                </ul>
                <a href="{{ config.checkout_starter }}" class="plan-btn dark" style="margin-top:auto;">GET STARTER ➔</a>
                <div class="spec-grid cols-2">
                    <div class="spec-cell"><span class="label">Cost Per</span><div>$0.04</div></div>
                    <div class="spec-cell"><span class="label">Speed</span><div>Instant</div></div>
                </div>
            </div>

            <div class="panel p-green">
                <span class="label">Unlimited</span>
                <div class="plan-name">Pro</div>
                <div class="plan-price">$4<span>/mo</span></div>
                <ul class="plan-features">
                    <li>Unlimited transcripts</li>
                    <li>All 1000+ platforms</li>
                    <li>Batch mode</li>
                    <li>CSV + JSON export</li>
                </ul>
                <a href="{{ config.checkout_pro }}" class="plan-btn green" style="margin-top:auto;">GET PRO ➔</a>
                <div class="spec-grid cols-2">
                    <div class="spec-cell"><span class="label">Limit</span><div>∞</div></div>
                    <div class="spec-cell"><span class="label">Speed</span><div>Instant</div></div>
                </div>
            </div>
        </div>

        <footer class="tech-footer">
            <div>TranscriptX Systems</div>
            <div style="text-align:right;">Built by <a href="https://google.com">x362 IIC</a></div>
        </footer>
    </div>
</body>
</html>
"""


# ── Profile Links Template ─────────────────────────────────

PROFILE_LINKS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Profile Link Extractor</title>
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --red: #B84B3F;
            --green: #709472;
            --grey: #C4C5C7;
            --ink: #0a0a0a;
            --f-wide: 'Michroma', sans-serif;
            --f-tech: 'Space Mono', monospace;
            --radius: 2rem;
            --bw: 1.5px;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:var(--bg); color:var(--ink); font-family:var(--f-tech); line-height:1.4; overflow-x:hidden; }

        .layout { max-width:800px; margin:0 auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; width:100%; }

        nav {
            display:flex; justify-content:space-between; align-items:center;
            padding:1rem 2rem; background:var(--grey); border-radius:100px;
        }
        .nav-logo { font-family:var(--f-wide); font-size:1.1rem; font-weight:900; text-decoration:none; color:var(--ink); }
        .nav-logo em { font-style:normal; font-size:0.5em; vertical-align:super; }
        .nav-links { display:flex; align-items:center; gap:0.5rem; }
        .nav-links a {
            color:var(--ink); text-decoration:none; font-size:0.7rem; font-weight:700;
            text-transform:uppercase; padding:0.5rem 1rem; border-radius:4px;
            border:1px solid transparent; transition:all 0.2s;
        }
        .nav-links a:hover { border-color:var(--ink); background:rgba(0,0,0,0.05); }
        .nav-badge {
            font-size:0.6rem; padding:0.4rem 0.8rem; border-radius:4px;
            font-weight:700; text-transform:uppercase; letter-spacing:0.5px;
        }
        .nav-badge.free { background:rgba(0,0,0,0.08); }
        .nav-badge.starter { background:rgba(66,85,212,0.15); color:#4255d4; }
        .nav-badge.pro { background:rgba(112,148,114,0.3); }

        .panel { border-radius:var(--radius); padding:2rem; }
        .label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; opacity:0.6; display:block; margin-bottom:0.3rem; }
        h1 { font-family:var(--f-wide); font-size:1.6rem; text-transform:uppercase; line-height:0.95; margin-bottom:1rem; }
        .sub { font-size:0.8rem; border-left:2px solid var(--ink); padding-left:1rem; margin-bottom:2rem; line-height:1.6; opacity:0.8; }

        .input-row { border:var(--bw) solid var(--ink); display:grid; grid-template-columns:1fr auto; }
        .input-row input {
            background:transparent; border:none; padding:1.2rem;
            font-family:var(--f-tech); font-size:0.9rem; color:var(--ink); outline:none;
        }
        .input-row input::placeholder { color:rgba(10,10,10,0.3); }
        .input-row button {
            background:var(--ink); color:var(--orange); border:none; padding:0 1.8rem;
            font-family:var(--f-wide); font-size:0.65rem; text-transform:uppercase; cursor:pointer;
        }
        .input-row button:hover { background:#333; }
        .input-row button:disabled { opacity:0.4; cursor:wait; }

        .options { display:flex; align-items:center; gap:1.2rem; margin-top:0.8rem; flex-wrap:wrap; }
        .options select {
            background:transparent; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:0.4rem 0.6rem; font-family:var(--f-tech); font-size:0.65rem;
        }

        .status { background:var(--grey); border-radius:var(--radius); padding:1.2rem 2rem; margin-bottom:0; display:none; }
        .status.on { display:flex; align-items:center; gap:10px; }
        .dot { width:6px; height:6px; border-radius:50%; background:var(--ink); animation:blink 1s ease infinite; flex-shrink:0; }
        @keyframes blink { 50%{opacity:0.2} }
        .status-text { flex:1; font-size:0.75rem; }
        .stop-btn {
            background:var(--red); color:#fff; border:none; padding:6px 14px;
            font-family:var(--f-tech); font-size:0.6rem; text-transform:uppercase; cursor:pointer;
            border-radius:4px;
        }
        .stop-btn:hover { opacity:0.8; }
        .counter {
            font-family:var(--f-wide); font-size:2rem; font-weight:700;
            min-width:60px; text-align:center;
        }

        .results { background:var(--grey); border-radius:var(--radius); padding:2rem; display:none; }
        .results.on { display:block; }
        .results-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:8px; }
        .results-head h2 { font-family:var(--f-wide); font-size:0.9rem; text-transform:uppercase; }
        .btn-row { display:flex; gap:6px; }
        .btn-sm {
            background:transparent; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:4px 12px; font-family:var(--f-tech); font-size:0.6rem; text-transform:uppercase; cursor:pointer;
        }
        .btn-sm:hover { background:var(--ink); color:var(--orange); }
        .btn-sm.green { border-color:var(--green); }
        .btn-sm.green:hover { background:var(--green); color:#fff; }

        .link-list {
            max-height:50vh; overflow-y:auto; border:var(--bw) solid var(--ink);
            padding:1rem; font-size:0.72rem; line-height:2; word-break:break-all;
        }
        .link-list a { color:var(--ink); text-decoration:none; display:block; opacity:0.8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .link-list a:hover { opacity:1; text-decoration:underline; }
        .link-list a.new { animation:fadeIn 0.3s ease; }
        @keyframes fadeIn { from{opacity:0;transform:translateX(-8px)} to{opacity:0.8;transform:none} }

        .err { background:var(--red); color:#fff; border-radius:var(--radius); padding:1.2rem 2rem; font-size:0.8rem; display:none; }
        .err.on { display:block; }

        .tech-footer {
            border:1px solid #333; color:#555; padding:1.5rem 2rem; font-size:0.6rem;
            text-transform:uppercase; display:flex; justify-content:space-between; letter-spacing:0.05em;
        }
        .tech-footer a { color:#555; text-decoration:none; }
        .tech-footer a:hover { color:var(--orange); }

        .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); z-index:100; justify-content:center; align-items:center; }
        .modal-overlay.open { display:flex; }
        .modal-box { background:var(--grey); border-radius:var(--radius); padding:2rem; width:90%; max-width:380px; text-align:center; }
        .modal-title { font-family:var(--f-wide); font-size:0.9rem; text-transform:uppercase; margin-bottom:4px; }
        .modal-sub { font-size:0.75rem; opacity:0.6; }
        .modal-input {
            width:100%; margin-top:1rem; background:transparent; border:var(--bw) solid var(--ink);
            padding:1rem; font-family:var(--f-tech); font-size:0.85rem; color:var(--ink); outline:none;
        }
        .modal-input::placeholder { color:rgba(10,10,10,0.35); }
        .modal-btn {
            width:100%; margin-top:0.8rem; background:var(--ink); color:var(--orange); border:none;
            padding:1rem; font-family:var(--f-wide); font-size:0.7rem; text-transform:uppercase; cursor:pointer;
        }
        .modal-btn:disabled { opacity:0.4; cursor:not-allowed; }
        .modal-err { color:var(--red); font-size:0.7rem; margin-top:0.5rem; min-height:1.2em; }
        .auth-tab {
            flex:1; background:transparent; border:var(--bw) solid var(--ink); padding:0.7rem;
            font-family:var(--f-wide); font-size:0.6rem; text-transform:uppercase; cursor:pointer;
            color:var(--ink); opacity:0.4; transition:all 0.2s;
        }
        .auth-tab.active { opacity:1; background:var(--ink); color:var(--orange); }

        @media (max-width:600px) {
            body { padding:0; }
            .layout { padding:0.5rem; gap:0.5rem; }
            nav { padding:0.6rem 1rem; border-radius:60px; }
            .nav-logo { font-size:0.85rem; }
            .nav-links { gap:0.2rem; }
            .nav-links a { font-size:0.55rem; padding:0.35rem 0.5rem; }
            .nav-badge { font-size:0.5rem; padding:0.3rem 0.5rem; }
            .panel { padding:1.5rem; border-radius:1.2rem; }
            h1 { font-size:1.2rem; }
            .input-row { grid-template-columns:1fr; }
            .input-row button { padding:0.9rem 1.5rem; }
            .results { padding:1.2rem; border-radius:1.2rem; }
            .status { border-radius:1.2rem; padding:1rem; }
            .modal-box { padding:1.5rem; border-radius:1rem; width:95%; }
            .tech-footer { flex-direction:column; gap:0.5rem; text-align:center; padding:1rem; font-size:0.55rem; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <nav>
            <a class="nav-logo" href="/">TRANSCRIPTX<em>&reg;</em></a>
            <div class="nav-links">
                {% if user.logged_in %}
                <span class="nav-badge {{ user.plan }}">{{ user.plan_name }} — {{ user.credits_label }}</span>
                {% if user.plan != 'free' %}
                <a href="{{ config.customer_portal }}">Billing</a>
                {% else %}
                <a href="/pricing">Upgrade</a>
                {% endif %}
                <a href="/">Transcribe</a>
                <a href="#" onclick="logout();return false">Logout</a>
                {% else %}
                <a href="/">Transcribe</a>
                <a href="#" onclick="showAuth('login');return false">Login</a>
                <a href="#" onclick="showAuth('signup');return false">Sign Up</a>
                {% endif %}
            </div>
        </nav>

        <div class="panel" style="background:var(--orange);">
            <span class="label">Profile Link Extractor</span>
            <h1>Get All<br>Video Links</h1>
            <div class="sub">Paste a TikTok, YouTube, Instagram, or X profile URL. Links stream in live — no waiting for all of them. <strong>1 credit per 5 links.</strong></div>
            <span class="label">Profile URL</span>
            <div class="input-row">
                <input type="text" id="url" placeholder="https://tiktok.com/@username" onkeydown="if(event.key==='Enter')go()">
                <button id="btn" onclick="go()">EXTRACT ➔</button>
            </div>
            <div class="options">
                <span class="label" style="margin:0">Limit:</span>
                <select id="limit">
                    <option value="0">All videos</option>
                    <option value="10" selected>Last 10</option>
                    <option value="25">Last 25</option>
                    <option value="50">Last 50</option>
                    <option value="100">Last 100</option>
                    <option value="200">Last 200</option>
                    <option value="500">Last 500</option>
                </select>
            </div>
        </div>

        <div class="status" id="status">
            <div class="dot"></div>
            <span class="status-text" id="msg">Extracting links...</span>
            <div class="counter" id="liveCount">0</div>
            <button class="stop-btn" onclick="stop()">Stop</button>
        </div>

        <div class="err" id="err"></div>

        <div class="results" id="results">
            <div class="results-head">
                <h2><span id="count">0</span> Links Found</h2>
                <div class="btn-row">
                    <button class="btn-sm" onclick="copyAll()">Copy All</button>
                    <button class="btn-sm green" onclick="downloadTxt()">Download .txt</button>
                </div>
            </div>
            <div class="link-list" id="links"></div>
        </div>

        <!-- Auth modal -->
        <div class="modal-overlay" id="authModal" onclick="if(event.target===this)hideAuth()">
            <div class="modal-box">
                <div id="authTabs" style="display:flex;gap:0;margin-bottom:1.2rem;">
                    <button class="auth-tab active" id="tabLogin" onclick="switchTab('login')">LOG IN</button>
                    <button class="auth-tab" id="tabSignup" onclick="switchTab('signup')">SIGN UP</button>
                </div>
                <div id="loginForm">
                    <input type="email" class="modal-input" id="loginEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="loginPassword" placeholder="Password" autocomplete="current-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doLogin()">
                    <div class="modal-err" id="loginErr"></div>
                    <button class="modal-btn" onclick="doLogin()">LOG IN ➔</button>
                </div>
                <div id="signupForm" style="display:none;">
                    <input type="email" class="modal-input" id="signupEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="signupPassword" placeholder="Password (6+ chars)" autocomplete="new-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doSignup()">
                    <div class="modal-err" id="signupErr"></div>
                    <button class="modal-btn" onclick="doSignup()">SIGN UP ➔</button>
                </div>
                <div id="verifyForm" style="display:none;">
                    <div class="modal-title">Check Your Email</div>
                    <div class="modal-sub" id="verifySub">Enter the 6-digit code we sent</div>
                    <input type="text" class="modal-input" id="verifyCode" placeholder="000000" maxlength="6" style="text-align:center;font-size:1.5rem;letter-spacing:0.4em;" onkeydown="if(event.key==='Enter')doVerify()">
                    <div class="modal-err" id="verifyErr"></div>
                    <button class="modal-btn" onclick="doVerify()">VERIFY ➔</button>
                    <div style="margin-top:0.8rem;text-align:center;">
                        <a href="#" onclick="resendCode();return false" style="font-size:0.7rem;color:var(--ink);opacity:0.5;">Resend code</a>
                    </div>
                </div>
            </div>
        </div>

        <footer class="tech-footer">
            <div>TranscriptX Systems</div>
            <div style="text-align:right;">Built by <a href="https://google.com">x362 IIC</a></div>
        </footer>
    </div>

    <script>
        let allLinks = [];
        let eventSource = null;

        function go() {
            {% if not user.logged_in %}
            showAuth('signup');
            return;
            {% endif %}

            const url = document.getElementById('url').value.trim();
            if (!url) return;

            const limit = document.getElementById('limit').value;
            const btn = document.getElementById('btn');
            const status = document.getElementById('status');
            const err = document.getElementById('err');
            const results = document.getElementById('results');
            const linksEl = document.getElementById('links');

            allLinks = [];
            linksEl.innerHTML = '';
            btn.disabled = true;
            err.classList.remove('on');
            results.classList.add('on');
            status.classList.add('on');
            document.getElementById('msg').textContent = 'Extracting links...';
            document.getElementById('liveCount').textContent = '0';
            document.getElementById('count').textContent = '0';

            if (eventSource) eventSource.close();

            const params = new URLSearchParams({url, limit});
            eventSource = new EventSource(`/api/profile-links?${params}`);

            eventSource.onmessage = function(e) {
                const d = JSON.parse(e.data);

                if (d.type === 'link') {
                    allLinks.push(d.url);
                    document.getElementById('liveCount').textContent = d.n;
                    document.getElementById('count').textContent = d.n;

                    const a = document.createElement('a');
                    a.href = d.url;
                    a.target = '_blank';
                    a.textContent = d.url;
                    a.className = 'new';
                    linksEl.appendChild(a);
                    linksEl.scrollTop = linksEl.scrollHeight;
                }
                else if (d.type === 'done') {
                    finish(`Done — ${d.count} links extracted` + (d.credits_used ? ` (${d.credits_used} credit${d.credits_used > 1 ? 's' : ''})` : ''));
                    updateCredits();
                }
                else if (d.type === 'error') {
                    finish();
                    err.textContent = d.msg;
                    err.classList.add('on');
                    if (allLinks.length === 0) results.classList.remove('on');
                    updateCredits();
                }
            };

            eventSource.onerror = function() {
                finish();
                if (allLinks.length === 0) {
                    err.textContent = 'Connection lost. Try again.';
                    err.classList.add('on');
                    results.classList.remove('on');
                }
                updateCredits();
            };
        }

        function stop() {
            if (eventSource) eventSource.close();
            finish('Stopped');
            updateCredits();
        }

        function finish(msg) {
            if (eventSource) { eventSource.close(); eventSource = null; }
            document.getElementById('btn').disabled = false;
            document.getElementById('status').classList.remove('on');
            if (msg) document.getElementById('msg').textContent = msg;
        }

        function copyAll() {
            navigator.clipboard.writeText(allLinks.join('\\n'));
            event.target.textContent = 'Copied!';
            setTimeout(() => event.target.textContent = 'Copy All', 1500);
        }

        function downloadTxt() {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(new Blob([allLinks.join('\\n')], {type:'text/plain'}));
            a.download = 'profile-links.txt';
            a.click();
        }

        async function updateCredits() {
            try {
                const r = await fetch('/api/me');
                const u = await r.json();
                const badge = document.querySelector('.nav-badge');
                if (badge) {
                    badge.textContent = `${u.plan_name} — ${u.credits_label}`;
                    badge.className = `nav-badge ${u.plan}`;
                }
            } catch(e) {}
        }

        let authEmail = '';
        function showAuth(tab) {
            document.getElementById('authModal').classList.add('open');
            switchTab(tab || 'login');
        }
        function hideAuth() {
            document.getElementById('authModal').classList.remove('open');
            document.getElementById('loginErr').textContent = '';
            document.getElementById('signupErr').textContent = '';
            document.getElementById('verifyErr').textContent = '';
        }
        function switchTab(tab) {
            var le = document.getElementById('loginEmail'), se = document.getElementById('signupEmail');
            if (tab === 'signup') se.value = le.value;
            if (tab === 'login') le.value = se.value;
            document.getElementById('loginForm').style.display = tab === 'login' ? '' : 'none';
            document.getElementById('signupForm').style.display = tab === 'signup' ? '' : 'none';
            document.getElementById('verifyForm').style.display = tab === 'verify' ? '' : 'none';
            document.getElementById('authTabs').style.display = tab === 'verify' ? 'none' : 'flex';
            document.getElementById('tabLogin').classList.toggle('active', tab === 'login');
            document.getElementById('tabSignup').classList.toggle('active', tab === 'signup');
            if (tab === 'login') le.focus();
            if (tab === 'signup') se.focus();
            if (tab === 'verify') document.getElementById('verifyCode').focus();
        }
        async function doSignup() {
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const err = document.getElementById('signupErr');
            err.textContent = '';
            if (!email) { err.textContent = 'Enter your email'; return; }
            if (password.length < 6) { err.textContent = 'Password must be 6+ characters'; return; }
            try {
                const r = await fetch('/api/signup', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email, password})
                });
                const d = await r.json();
                if (d.step === 'verify') {
                    authEmail = email;
                    document.getElementById('verifySub').textContent = 'Code sent to ' + email;
                    switchTab('verify');
                } else {
                    err.textContent = d.error || 'Something went wrong';
                }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }
        async function doVerify() {
            const code = document.getElementById('verifyCode').value.trim();
            const err = document.getElementById('verifyErr');
            err.textContent = '';
            if (code.length !== 6) { err.textContent = 'Enter the 6-digit code'; return; }
            try {
                const r = await fetch('/api/verify', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email: authEmail, code})
                });
                const d = await r.json();
                if (r.ok) { location.reload(); }
                else { err.textContent = d.error || 'Invalid code'; }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }
        async function resendCode() {
            if (!authEmail) return;
            try {
                await fetch('/api/resend-code', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email: authEmail})
                });
                document.getElementById('verifyErr').textContent = '';
                document.getElementById('verifySub').textContent = 'New code sent to ' + authEmail;
            } catch(e) {}
        }
        async function doLogin() {
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;
            const err = document.getElementById('loginErr');
            err.textContent = '';
            if (!email) { err.textContent = 'Enter your email'; return; }
            if (!password) { err.textContent = 'Enter your password'; return; }
            try {
                const r = await fetch('/api/login', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({email, password})
                });
                const d = await r.json();
                if (d.status === 'ok') { location.reload(); }
                else if (d.status === 'verify') {
                    authEmail = email;
                    document.getElementById('verifySub').textContent = 'Code sent to ' + email;
                    switchTab('verify');
                }
                else { err.textContent = d.error || 'Login failed'; }
            } catch(e) { err.textContent = 'Something went wrong'; }
        }
        async function logout() {
            await fetch('/api/logout', {method:'POST'});
            location.reload();
        }

    </script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"

    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set! Get one at https://console.groq.com")

    print(f"\n{'='*50}")
    print("⚡ TranscriptX")
    print(f"{'='*50}")
    print(f"\n   http://localhost:{port}\n")

    app.run(debug=debug, host="0.0.0.0", port=port)