"""
app.py — TranscriptX
======================
Flask app with Polar payments, SQLite credits, Groq transcription.
"""

import os
import uuid
import json
from dotenv import load_dotenv

load_dotenv()  # Load .env file automatically

from flask import Flask, request, jsonify, session, redirect, render_template_string
from database import init_db, PLANS, get_free_credits, use_free_credit
from database import create_or_update_user, cancel_user, get_user, get_user_credits, use_user_credit
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

# Initialize DB on startup
init_db()


# ── Helpers ─────────────────────────────────────────────────

def _get_session_id():
    """Get or create anonymous session ID."""
    if "sid" not in session:
        session["sid"] = uuid.uuid4().hex
    return session["sid"]


def _get_current_user():
    """Get current user info (paid or free)."""
    polar_id = session.get("polar_customer_id")

    if polar_id:
        user = get_user(polar_id)
        if user:
            plan = PLANS.get(user["plan"], PLANS["free"])
            credits = get_user_credits(polar_id)
            return {
                "type": "paid",
                "email": user["email"],
                "plan": user["plan"],
                "plan_name": plan.get("name", user["plan"].title()),
                "credits": credits,
                "credits_label": "Unlimited" if credits == -1 else str(credits),
                "batch": plan["batch"],
                "csv_export": plan["csv_export"],
            }

    # Free user
    sid = _get_session_id()
    credits = get_free_credits(sid)
    return {
        "type": "free",
        "email": None,
        "plan": "free",
        "plan_name": "Free",
        "credits": credits,
        "credits_label": str(credits),
        "batch": False,
        "csv_export": False,
    }


# ── API Routes ──────────────────────────────────────────────

@app.route("/api/extract", methods=["POST"])
def api_extract():
    """Extract transcript from a URL. Deducts 1 credit."""
    data = request.json or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"status": "error", "error": "No URL provided"}), 400

    if not url.startswith(("https://", "http://")):
        return jsonify({"status": "error", "error": "Invalid URL. Must start with https://"}), 400

    # Check credits
    user = _get_current_user()
    polar_id = session.get("polar_customer_id")

    if polar_id and user["type"] == "paid":
        if user["credits"] != -1 and user["credits"] <= 0:
            return jsonify({"status": "error", "error": "No credits remaining. Please upgrade your plan."}), 403
        if not use_user_credit(polar_id):
            return jsonify({"status": "error", "error": "No credits remaining."}), 403
    else:
        sid = _get_session_id()
        if not use_free_credit(sid):
            return jsonify({"status": "error", "error": "Free credits used up. Upgrade to keep transcribing!"}), 403

    # Process
    model = data.get("model", "whisper-large-v3-turbo")
    if model not in ("whisper-large-v3-turbo", "whisper-large-v3"):
        model = "whisper-large-v3-turbo"

    result = process_url(url, model=model)
    return jsonify(result)


@app.route("/api/me")
def api_me():
    """Get current user info + credits."""
    return jsonify(_get_current_user())


# ── Polar Webhooks ──────────────────────────────────────────

@app.route("/webhooks/polar", methods=["POST"])
def polar_webhook():
    """
    Handle Polar subscription events.
    Polar uses Standard Webhooks (svix) for signatures.
    For production, install `standardwebhooks` package for proper verification.
    """
    payload = request.get_data()

    # TODO: For production, verify with standardwebhooks package:
    #   from standardwebhooks.webhooks import Webhook
    #   wh = Webhook(POLAR_WEBHOOK_SECRET)
    #   wh.verify(payload, request.headers)

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
    """After Polar checkout, link the customer to this session."""
    customer_id = request.args.get("customer_id", "")
    if customer_id:
        session["polar_customer_id"] = customer_id
    return redirect("/")


@app.route("/api/login", methods=["POST"])
def api_login():
    """Link session to existing paid account by email."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"status": "error", "error": "Enter your email"}), 400

    from database import get_db
    with get_db() as db:
        row = db.execute(
            "SELECT polar_customer_id, plan FROM users WHERE LOWER(email) = ?",
            (email,)
        ).fetchone()

    if not row or row["plan"] == "free":
        return jsonify({"status": "error", "error": "No active subscription found for this email."}), 404

    session["polar_customer_id"] = row["polar_customer_id"]
    return jsonify({"status": "ok", "plan": row["plan"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Clear session."""
    session.pop("polar_customer_id", None)
    return jsonify({"status": "ok"})


# ── Admin ───────────────────────────────────────────────────

ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")

@app.route("/admin")
def admin():
    """Admin dashboard — protected by ?key= param."""
    if request.args.get("key") != ADMIN_KEY:
        return "Not found", 404

    from database import get_db
    with get_db() as db:
        users = [dict(r) for r in db.execute(
            "SELECT polar_customer_id, email, plan, credits_used, credits_reset_at, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()]

        sessions = [dict(r) for r in db.execute(
            "SELECT session_id, credits_used, credits_reset_at, created_at FROM free_sessions ORDER BY created_at DESC LIMIT 100"
        ).fetchall()]

        stats = {
            "total_users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "paid_users": db.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'").fetchone()[0],
            "starter": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'starter'").fetchone()[0],
            "pro": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'pro'").fetchone()[0],
            "free_sessions": db.execute("SELECT COUNT(*) FROM free_sessions").fetchone()[0],
            "total_free_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM free_sessions").fetchone()[0],
            "total_paid_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM users").fetchone()[0],
        }

    return render_template_string(ADMIN_TEMPLATE, users=users, sessions=sessions, stats=stats)


ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Admin</title>
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
                <div class="stat-num" data-count="{{ stats.free_sessions }}">0</div>
                <div class="stat-lbl">Free Sessions</div>
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
                            stroke-dashoffset="{{ 100 - ([((stats.paid_users / (stats.paid_users + stats.free_sessions)) * 100) if (stats.paid_users + stats.free_sessions) > 0 else 0, 100] | min) }}"/>
                    </svg>
                    <div class="circle-label">{{ ((stats.paid_users / (stats.paid_users + stats.free_sessions)) * 100) | int if (stats.paid_users + stats.free_sessions) > 0 else 0 }}%</div>
                </div>
                <div>
                    <div class="chart-title">Conversion Rate</div>
                    <div class="chart-sub">{{ stats.paid_users }} paid / {{ stats.paid_users + stats.free_sessions }} total</div>
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

        <!-- Free Sessions -->
        <div class="section-head">
            <div class="section-title">Free Sessions</div>
            <div class="section-count">{{ stats.free_sessions }}</div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr><th>Session</th><th>Usage</th><th>Resets</th><th>Created</th></tr>
                </thead>
                <tbody>
                    {% for s in sessions %}
                    <tr>
                        <td class="mono" style="opacity:1">{{ s.session_id[:16] }}…</td>
                        <td>
                            <div class="usage-bar-wrap">
                                <span class="mono">{{ s.credits_used }}</span>
                                <div class="usage-bar"><div class="usage-bar-fill orange" style="width:{{ (s.credits_used / 3 * 100) | int }}%"></div></div>
                                <span class="mono">/ 3</span>
                            </div>
                        </td>
                        <td class="mono">{{ s.credits_reset_at[:10] if s.credits_reset_at else '—' }}</td>
                        <td class="mono">{{ s.created_at[:10] if s.created_at else '—' }}</td>
                    </tr>
                    {% endfor %}
                    {% if not sessions %}<tr><td colspan="4" class="empty-row">No free sessions yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <footer class="tech-footer">
            <div>TranscriptX Admin<br>System Dashboard</div>
            <div style="text-align:right;">Built by Attention Factory</div>
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


# ── Main Template ──────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Instant Transcripts from Any Video</title>
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

        .layout { max-width:1100px; margin:0 auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; }

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
        .panel { border-radius:var(--radius); padding:2rem; position:relative; overflow:hidden; display:flex; flex-direction:column; min-width:0; }
        .p-orange { background:var(--orange); }
        .p-red { background:var(--red); }
        .p-green { background:var(--green); }
        .p-grey { background:var(--grey); }

        .label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; opacity:0.6; margin-bottom:0.3rem; display:block; }

        /* ── Hero split ── */
        .hero { display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:1rem; min-height:65vh; }

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
        }
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
        .meter-box { border:var(--bw) solid var(--ink); padding:0.8rem 1rem; margin-top:0.8rem; display:flex; justify-content:space-between; align-items:center; }
        .digital { font-size:1rem; font-weight:700; border:var(--bw) solid var(--ink); padding:0.2rem 0.6rem; background:rgba(255,255,255,0.1); }

        .ticker-wrap { overflow:hidden; border-top:var(--bw) solid var(--ink); padding-top:1rem; margin-top:auto; }
        .ticker-items { display:flex; gap:6px; animation:scroll 25s linear infinite; width:max-content; }
        .ticker-items:hover { animation-play-state:paused; }
        @keyframes scroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
        .ticker-item {
            padding:4px 10px; border:var(--bw) solid var(--ink); font-size:0.55rem;
            font-weight:700; text-transform:uppercase; white-space:nowrap; letter-spacing:0.03em;
        }

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

        /* ── Login modal ── */
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
        .modal-err { color:var(--red); font-size:0.7rem; margin-top:0.5rem; min-height:1.2em; }

        /* ── Footer ── */
        .tech-footer {
            border:1px solid #333; color:#555; padding:1.5rem 2rem; font-size:0.6rem;
            text-transform:uppercase; display:flex; justify-content:space-between; letter-spacing:0.05em;
        }
        .tech-footer a { color:#555; text-decoration:none; }
        .tech-footer a:hover { color:var(--orange); }

        @media (max-width:800px) {
            .hero { grid-template-columns:1fr; min-height:auto; }
            .hero-h1 { font-size:2rem; }
            .nav { padding:0.8rem 1.2rem; }
            .nav-links a { display:none; }
            .nav-links .nav-badge { display:inline-block; }
            .spec-grid.cols-4 { grid-template-columns:repeat(2,1fr); }
            .layout { padding:0.6rem; gap:0.6rem; }
            .panel { padding:1.2rem; border-radius:1.2rem; }
            .hero-top { flex-direction:column; gap:0.3rem; padding-bottom:0.6rem; margin-bottom:1rem; }
            .hero-sub { font-size:0.78rem; }
            .input-machine input { padding:1rem; font-size:0.85rem; }
            .input-machine button { padding:0 1.2rem; font-size:0.6rem; }
            .controls { font-size:0.6rem; }
            .stat-block h2 { font-size:1.1rem; }
            .meter-box { padding:0.6rem 0.8rem; font-size:0.7rem; }
            .digital { font-size:0.8rem; padding:0.15rem 0.5rem; }
            .ticker-item { font-size:0.5rem; padding:3px 8px; }
            .tech-footer { flex-direction:column; gap:0.8rem; padding:1.2rem; font-size:0.55rem; text-align:center; }
            .tech-footer div { text-align:center !important; }
            .modal-box { padding:1.5rem; border-radius:1.2rem; }
            .result-card { padding:1.2rem; border-radius:1.2rem; }
            .export-btn { padding:0.5rem 0.8rem; font-size:0.6rem; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <!-- Nav -->
        <nav>
            <div class="nav-logo">TRANSCRIPTX<em>®</em></div>
            <div class="nav-links">
                <span class="nav-badge {{ user.plan }}">{{ user.plan_name }} — {{ user.credits_label }}</span>
                {% if user.type == 'paid' %}
                <a href="{{ config.customer_portal }}">Billing</a>
                <a href="#" onclick="logout();return false">Logout</a>
                {% else %}
                <a href="#" onclick="showLogin();return false">Login</a>
                <a href="/pricing">Pricing</a>
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
                        <span class="label" style="margin:0">Groq Whisper • 216x Realtime</span>
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
                        <span class="digital">WHISPER</span>
                    </div>
                    <div class="meter-box" style="margin-top:4px;">
                        <span class="label" style="margin:0">Accuracy</span>
                        <span class="digital">99.2%</span>
                    </div>
                    <div class="ticker-wrap">
                        <div class="ticker-items">
                            <span class="ticker-item">YouTube</span>
                            <span class="ticker-item">TikTok</span>
                            <span class="ticker-item">Instagram</span>
                            <span class="ticker-item">X / Twitter</span>
                            <span class="ticker-item">Facebook</span>
                            <span class="ticker-item">LinkedIn</span>
                            <span class="ticker-item">Reddit</span>
                            <span class="ticker-item">Vimeo</span>
                            <span class="ticker-item">Twitch</span>
                            <span class="ticker-item">Rumble</span>
                            <span class="ticker-item">Threads</span>
                            <span class="ticker-item">SoundCloud</span>
                            <span class="ticker-item">Bilibili</span>
                            <span class="ticker-item">Snapchat</span>
                            <span class="ticker-item">1000+ more</span>
                            <span class="ticker-item">YouTube</span>
                            <span class="ticker-item">TikTok</span>
                            <span class="ticker-item">Instagram</span>
                            <span class="ticker-item">X / Twitter</span>
                            <span class="ticker-item">Facebook</span>
                            <span class="ticker-item">LinkedIn</span>
                            <span class="ticker-item">Reddit</span>
                            <span class="ticker-item">Vimeo</span>
                            <span class="ticker-item">Twitch</span>
                            <span class="ticker-item">Rumble</span>
                            <span class="ticker-item">Threads</span>
                            <span class="ticker-item">SoundCloud</span>
                            <span class="ticker-item">Bilibili</span>
                            <span class="ticker-item">Snapchat</span>
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

        <!-- Login modal -->
        <div class="modal-overlay" id="loginModal" onclick="if(event.target===this)hideLogin()">
            <div class="modal-box">
                <div class="modal-title">Restore Subscription</div>
                <div class="modal-sub">Enter the email used at checkout</div>
                <input type="email" class="modal-input" id="loginEmail" placeholder="you@email.com" onkeydown="if(event.key==='Enter')doLogin()">
                <div class="modal-err" id="loginErr"></div>
                <button class="modal-btn" onclick="doLogin()">RESTORE ➔</button>
            </div>
        </div>

        <!-- Footer -->
        <footer class="tech-footer">
            <div>TranscriptX Systems<br>Powered by Groq Whisper</div>
            <div style="text-align:right;">Built by <a href="#">Attention Factory</a><br>1000+ platforms supported</div>
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

            for (let i = 0; i < urls.length; i++) {
                msg.textContent = urls.length > 1 ? `Processing ${i+1}/${urls.length}...` : 'Transcribing...';
                prog.style.width = `${(i/urls.length)*100}%`;

                try {
                    const r = await fetch('/api/extract', {
                        method: 'POST',
                        headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({url: urls[i], model})
                    });
                    const d = await r.json();

                    if (r.status === 403) {
                        showUpgrade(d.error);
                        break;
                    }

                    all.push(d);
                    render(d);
                    updateCredits();
                } catch(e) {
                    all.push({url:urls[i], status:'error', error:e.message});
                    render({url:urls[i], status:'error', error:e.message});
                }
                prog.style.width = `${((i+1)/urls.length)*100}%`;
            }

            btn.disabled = false;
            btn.classList.remove('loading');
            status.classList.remove('on');
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

        function showLogin(){document.getElementById('loginModal').classList.add('open');document.getElementById('loginEmail').focus();}
        function hideLogin(){document.getElementById('loginModal').classList.remove('open');document.getElementById('loginErr').textContent='';}

        async function doLogin(){
            const email=document.getElementById('loginEmail').value.trim();
            const err=document.getElementById('loginErr');
            if(!email){err.textContent='Enter your email';return;}
            err.textContent='';
            try{
                const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})});
                const d=await r.json();
                if(r.ok){location.reload();}
                else{err.textContent=d.error||'Not found';}
            }catch(e){err.textContent='Something went wrong';}
        }

        async function logout(){
            await fetch('/api/logout',{method:'POST'});
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
            <a class="back" href="/">← Back</a>
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
                    <li>Groq Whisper large-v3</li>
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
                    <div class="spec-cell"><span class="label">Speed</span><div>216x RT</div></div>
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
                    <div class="spec-cell"><span class="label">Speed</span><div>216x RT</div></div>
                </div>
            </div>
        </div>

        <footer class="tech-footer">
            <div>TranscriptX Systems<br>Powered by Groq Whisper</div>
            <div style="text-align:right;">Built by Attention Factory</div>
        </footer>
    </div>
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