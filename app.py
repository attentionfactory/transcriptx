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


# ── UI ──────────────────────────────────────────────────────

@app.route("/")
def index():
    user = _get_current_user()
    return render_template_string(HTML_TEMPLATE, user=user, config={
        "checkout_starter": POLAR_CHECKOUT_STARTER,
        "checkout_pro": POLAR_CHECKOUT_PRO,
        "customer_portal": POLAR_CUSTOMER_PORTAL,
    })


# ── HTML Template ───────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Instant Transcripts from Any Video</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #06060a;
            --bg-card: #0d0d14;
            --bg-input: #0a0a10;
            --accent: #5046e5;
            --accent-bright: #7c6ff7;
            --accent-glow: rgba(80, 70, 229, 0.25);
            --green: #10b981;
            --green-glow: rgba(16, 185, 129, 0.2);
            --orange: #f59e0b;
            --red: #ef4444;
            --text: #eeeef5;
            --text-dim: #7a7a95;
            --text-faint: #44445a;
            --border: #1a1a2e;
            --border-light: #25253a;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }

        /* ── Noise texture overlay ── */
        body::after {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: -1;
        }

        /* ── Ambient glow ── */
        .glow-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(120px);
            pointer-events: none;
            z-index: -1;
        }
        .glow-orb.one { width: 500px; height: 500px; background: rgba(80,70,229,0.08); top: -10%; left: -5%; }
        .glow-orb.two { width: 400px; height: 400px; background: rgba(16,185,129,0.05); bottom: -10%; right: -5%; }

        .container { max-width: 820px; margin: 0 auto; padding: 40px 20px 60px; }

        /* ── Header ── */
        .header { text-align: center; margin-bottom: 40px; }

        .logo {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -2px;
        }
        .logo em { font-style: normal; color: var(--accent-bright); }

        .tagline { color: var(--text-dim); font-size: 0.95rem; margin-top: 6px; font-weight: 300; }

        /* ── Platform ticker ── */
        .ticker-wrap {
            margin-top: 18px;
            overflow: hidden;
            position: relative;
            width: 100%;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        .ticker-wrap::before, .ticker-wrap::after {
            content: '';
            position: absolute;
            top: 0;
            width: 60px;
            height: 100%;
            z-index: 2;
            pointer-events: none;
        }
        .ticker-wrap::before { left: 0; background: linear-gradient(to right, var(--bg), transparent); }
        .ticker-wrap::after { right: 0; background: linear-gradient(to left, var(--bg), transparent); }

        .ticker { overflow: hidden; }
        .ticker-items {
            display: flex;
            gap: 6px;
            animation: tickerScroll 30s linear infinite;
            width: max-content;
        }
        .ticker-items:hover { animation-play-state: paused; }

        @keyframes tickerScroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        .ticker-item {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 500;
            color: var(--text-dim);
            white-space: nowrap;
            transition: border-color 0.2s, color 0.2s;
        }
        .ticker-item:hover { border-color: var(--accent); color: var(--accent-bright); }
        .ti-icon { font-size: 0.65rem; color: var(--text-faint); }

        /* ── User bar ── */
        .user-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .credit-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }

        .credit-badge.free { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); color: var(--orange); }
        .credit-badge.starter { background: var(--accent-glow); border: 1px solid rgba(80,70,229,0.3); color: var(--accent-bright); }
        .credit-badge.pro { background: var(--green-glow); border: 1px solid rgba(16,185,129,0.3); color: var(--green); }

        .plan-link {
            font-size: 0.75rem;
            color: var(--text-faint);
            text-decoration: none;
            border-bottom: 1px dashed var(--text-faint);
            transition: color 0.2s;
        }
        .plan-link:hover { color: var(--accent-bright); border-color: var(--accent-bright); }

        /* ── Input card ── */
        .input-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 28px;
            margin-bottom: 28px;
        }

        .input-row { display: flex; gap: 10px; }

        .url-input {
            flex: 1;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 13px 16px;
            color: var(--text);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .url-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
        .url-input::placeholder { color: var(--text-faint); }
        .url-input:disabled { opacity: 0.5; }

        .go-btn {
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 13px 24px;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
            letter-spacing: 0.5px;
        }
        .go-btn:hover:not(:disabled) { background: var(--accent-bright); transform: translateY(-1px); box-shadow: 0 4px 20px var(--accent-glow); }
        .go-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .go-btn.loading { color: transparent; position: relative; }
        .go-btn.loading::after {
            content: '';
            position: absolute;
            width: 18px; height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: #fff;
            border-radius: 50%;
            top: 50%; left: 50%;
            margin: -9px 0 0 -9px;
            animation: spin 0.5s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 14px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .model-picker {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: var(--text-faint);
        }
        .model-picker select {
            background: var(--bg-input);
            border: 1px solid var(--border);
            color: var(--text-dim);
            padding: 5px 8px;
            border-radius: 5px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.75rem;
            outline: none;
        }

        /* Batch toggle */
        .toggle-wrap {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: var(--text-faint);
            cursor: pointer;
        }
        .toggle-wrap input { display: none; }
        .toggle-track {
            width: 32px; height: 18px;
            background: var(--border);
            border-radius: 9px;
            position: relative;
            transition: background 0.2s;
        }
        .toggle-track::after {
            content: '';
            width: 14px; height: 14px;
            background: var(--text-faint);
            border-radius: 50%;
            position: absolute;
            top: 2px; left: 2px;
            transition: all 0.2s;
        }
        .toggle-wrap input:checked + .toggle-track { background: var(--accent); }
        .toggle-wrap input:checked + .toggle-track::after { left: 16px; background: #fff; }

        .batch-area { display: none; margin-top: 14px; }
        .batch-area.open { display: block; }
        .batch-textarea {
            width: 100%;
            min-height: 100px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 14px;
            color: var(--text);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            line-height: 1.6;
            outline: none;
            resize: vertical;
        }
        .batch-textarea:focus { border-color: var(--accent); }
        .batch-textarea::placeholder { color: var(--text-faint); }

        /* ── Status ── */
        .status { display: none; margin-bottom: 20px; }
        .status.on { display: flex; align-items: center; gap: 10px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 12px 18px; font-size: 0.82rem; color: var(--text-dim); }
        .status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-bright); animation: blink 1.2s ease infinite; }
        @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.2; } }
        .progress-track { flex:1; height:3px; background:var(--border); border-radius:2px; overflow:hidden; }
        .progress-bar { height:100%; background:var(--accent); border-radius:2px; transition: width 0.4s; width:0; }

        /* ── Export bar ── */
        .export-bar { display:none; justify-content:center; gap:10px; margin-bottom:20px; }
        .export-bar.on { display:flex; }
        .export-btn {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-dim);
            padding: 8px 16px;
            border-radius: 6px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .export-btn:hover { border-color: var(--accent); color: var(--accent-bright); }

        /* ── Result cards ── */
        .result-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 14px;
            animation: cardIn 0.4s ease;
        }
        @keyframes cardIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
        .result-card.err { border-left: 3px solid var(--red); }

        .result-url { font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:var(--text-faint); margin-bottom:14px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .result-url a { color:var(--accent-bright); text-decoration:none; }

        .stats-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(90px,1fr)); gap:10px; margin-bottom:16px; }
        .stat { text-align:center; padding:10px; background:var(--bg-input); border-radius:8px; }
        .stat-val { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:700; }
        .stat-lbl { font-size:0.6rem; color:var(--text-faint); text-transform:uppercase; letter-spacing:1px; margin-top:3px; }

        .transcript-box { background:var(--bg-input); border:1px solid var(--border); border-radius:8px; padding:16px; }
        .transcript-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
        .transcript-label { font-size:0.65rem; text-transform:uppercase; letter-spacing:1px; color:var(--text-faint); }
        .copy-btn {
            background:none; border:1px solid var(--border); color:var(--text-faint);
            padding:3px 10px; border-radius:4px; font-size:0.65rem; cursor:pointer;
            font-family:'Outfit',sans-serif; transition:all 0.2s;
        }
        .copy-btn:hover { border-color:var(--accent); color:var(--accent-bright); }
        .copy-btn.ok { border-color:var(--green); color:var(--green); }

        .transcript-text { font-size:0.88rem; line-height:1.7; color:var(--text-dim); }

        /* ── Pricing section ── */
        .pricing { margin-top: 40px; text-align: center; }
        .pricing h2 { font-size: 1.3rem; margin-bottom: 6px; }
        .pricing .sub { color: var(--text-dim); font-size: 0.85rem; margin-bottom: 24px; }

        .plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }

        .plan-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            transition: border-color 0.2s;
        }
        .plan-card:hover { border-color: var(--border-light); }
        .plan-card.featured { border-color: var(--accent); box-shadow: 0 0 30px var(--accent-glow); }

        .plan-name { font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
        .plan-price { font-family:'JetBrains Mono',monospace; font-size: 1.8rem; font-weight: 700; }
        .plan-price span { font-size: 0.8rem; font-weight: 400; color: var(--text-dim); }
        .plan-features { list-style: none; margin: 16px 0; font-size: 0.8rem; color: var(--text-dim); }
        .plan-features li { padding: 4px 0; }
        .plan-features li::before { content: '✓ '; color: var(--green); }

        .plan-btn {
            display: inline-block;
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.82rem;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }
        .plan-btn.outline { background: none; border: 1px solid var(--border); color: var(--text-dim); }
        .plan-btn.primary { background: var(--accent); color: #fff; }
        .plan-btn.green { background: var(--green); color: #fff; }
        .plan-btn.primary:hover { background: var(--accent-bright); }
        .plan-btn.green:hover { background: #34d399; }

        .footer { text-align:center; padding:40px 0 10px; color:var(--text-faint); font-size:0.7rem; }

        /* ── Login modal ── */
        .modal-overlay {
            display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7);
            z-index:100; justify-content:center; align-items:center;
        }
        .modal-overlay.open { display:flex; }
        .modal-box {
            background:var(--bg-card); border:1px solid var(--border); border-radius:14px;
            padding:28px; width:90%; max-width:380px; text-align:center;
        }
        .modal-title { font-weight:700; font-size:1.1rem; margin-bottom:4px; }
        .modal-sub { color:var(--text-dim); font-size:0.82rem; }
        .modal-err { color:var(--red); font-size:0.75rem; margin-top:8px; min-height:1.2em; }

        @media (max-width:600px) {
            .container { padding: 20px 14px 40px; }
            .input-row { flex-direction:column; }
            .logo { font-size: 1.6rem; }
            .stats-grid { grid-template-columns: repeat(2,1fr); }
        }
    </style>
</head>
<body>
    <div class="glow-orb one"></div>
    <div class="glow-orb two"></div>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Transcript<em>X</em></div>
            <div class="tagline">Instant transcripts from any video. Just paste the link.</div>

            <!-- Platform ticker -->
            <div class="ticker-wrap">
                <div class="ticker">
                    <div class="ticker-items">
                        <span class="ticker-item"><span class="ti-icon">▶</span> YouTube</span>
                        <span class="ticker-item"><span class="ti-icon">♪</span> TikTok</span>
                        <span class="ticker-item"><span class="ti-icon">◉</span> Instagram</span>
                        <span class="ticker-item"><span class="ti-icon">✕</span> X / Twitter</span>
                        <span class="ticker-item"><span class="ti-icon">▣</span> Facebook</span>
                        <span class="ticker-item"><span class="ti-icon">◈</span> LinkedIn</span>
                        <span class="ticker-item"><span class="ti-icon">⬡</span> Reddit</span>
                        <span class="ticker-item"><span class="ti-icon">◎</span> Vimeo</span>
                        <span class="ticker-item"><span class="ti-icon">⬢</span> Twitch</span>
                        <span class="ticker-item"><span class="ti-icon">◆</span> Dailymotion</span>
                        <span class="ticker-item"><span class="ti-icon">▸</span> SoundCloud</span>
                        <span class="ticker-item"><span class="ti-icon">◇</span> Rumble</span>
                        <span class="ticker-item"><span class="ti-icon">✦</span> Threads</span>
                        <span class="ticker-item"><span class="ti-icon">◐</span> Pinterest</span>
                        <span class="ticker-item"><span class="ti-icon">▶</span> Bilibili</span>
                        <span class="ticker-item"><span class="ti-icon">◉</span> Snapchat</span>
                        <span class="ticker-item"><span class="ti-icon">♦</span> 1000+ more</span>
                        <!-- duplicate for seamless loop -->
                        <span class="ticker-item"><span class="ti-icon">▶</span> YouTube</span>
                        <span class="ticker-item"><span class="ti-icon">♪</span> TikTok</span>
                        <span class="ticker-item"><span class="ti-icon">◉</span> Instagram</span>
                        <span class="ticker-item"><span class="ti-icon">✕</span> X / Twitter</span>
                        <span class="ticker-item"><span class="ti-icon">▣</span> Facebook</span>
                        <span class="ticker-item"><span class="ti-icon">◈</span> LinkedIn</span>
                        <span class="ticker-item"><span class="ti-icon">⬡</span> Reddit</span>
                        <span class="ticker-item"><span class="ti-icon">◎</span> Vimeo</span>
                        <span class="ticker-item"><span class="ti-icon">⬢</span> Twitch</span>
                        <span class="ticker-item"><span class="ti-icon">◆</span> Dailymotion</span>
                        <span class="ticker-item"><span class="ti-icon">▸</span> SoundCloud</span>
                        <span class="ticker-item"><span class="ti-icon">◇</span> Rumble</span>
                        <span class="ticker-item"><span class="ti-icon">✦</span> Threads</span>
                        <span class="ticker-item"><span class="ti-icon">◐</span> Pinterest</span>
                        <span class="ticker-item"><span class="ti-icon">▶</span> Bilibili</span>
                        <span class="ticker-item"><span class="ti-icon">◉</span> Snapchat</span>
                        <span class="ticker-item"><span class="ti-icon">♦</span> 1000+ more</span>
                    </div>
                </div>
            </div>
            <div class="user-bar">
                <div class="credit-badge {{ user.plan }}" id="creditBadge">
                    {{ user.plan_name }} — {{ user.credits_label }} credits
                </div>
                {% if user.type == 'paid' %}
                <a href="{{ config.customer_portal }}" class="plan-link">Manage billing</a>
                <a href="#" class="plan-link" onclick="logout();return false">Log out</a>
                {% else %}
                <a href="#" class="plan-link" onclick="showLogin();return false">Already subscribed?</a>
                <a href="#pricing" class="plan-link">Upgrade</a>
                {% endif %}
            </div>
        </div>

        <!-- Input -->
        <div class="input-card">
            <div class="input-row">
                <input type="text" class="url-input" id="urlInput"
                       placeholder="Paste any video URL — Instagram, TikTok, YouTube, X..."
                       onkeydown="if(event.key==='Enter')go()">
                <button class="go-btn" id="goBtn" onclick="go()">Transcribe</button>
            </div>
            <div class="controls">
                <label class="toggle-wrap" id="batchWrap" style="{% if not user.batch %}opacity:0.4;pointer-events:none{% endif %}">
                    <input type="checkbox" id="batchToggle" onchange="toggleBatch()">
                    <div class="toggle-track"></div>
                    Batch {% if not user.batch %}(Starter+){% endif %}
                </label>
                <div class="model-picker">
                    <span>Model:</span>
                    <select id="modelSel">
                        <option value="whisper-large-v3-turbo" selected>turbo (fast)</option>
                        <option value="whisper-large-v3">large-v3 (best)</option>
                    </select>
                </div>
            </div>
            <div class="batch-area" id="batchArea">
                <textarea class="batch-textarea" id="batchUrls" placeholder="One URL per line..."></textarea>
            </div>
        </div>

        <!-- Status -->
        <div class="status" id="status">
            <div class="status-dot"></div>
            <span id="statusMsg">Processing...</span>
            <div class="progress-track"><div class="progress-bar" id="prog"></div></div>
        </div>

        <!-- Export -->
        <div class="export-bar" id="exportBar">
            <button class="export-btn" onclick="expCSV()">Export CSV</button>
            <button class="export-btn" onclick="expJSON()">Export JSON</button>
            <button class="export-btn" onclick="clearAll()">Clear</button>
        </div>

        <!-- Results -->
        <div id="results"></div>

        <!-- Pricing -->
        <div class="pricing" id="pricing">
            <h2>Simple pricing</h2>
            <div class="sub">Works with Instagram, TikTok, YouTube, X, and 1000+ more. Start free.</div>
            <div class="plans">
                <div class="plan-card">
                    <div class="plan-name">Free</div>
                    <div class="plan-price">$0</div>
                    <ul class="plan-features">
                        <li>3 transcripts / month</li>
                        <li>Any platform, any video</li>
                        <li>Groq Whisper large-v3</li>
                    </ul>
                    <div class="plan-btn outline" style="cursor:default">Current</div>
                </div>
                <div class="plan-card featured">
                    <div class="plan-name">Starter</div>
                    <div class="plan-price">$2<span>/mo</span></div>
                    <ul class="plan-features">
                        <li>50 transcripts / month</li>
                        <li>All 1000+ platforms</li>
                        <li>Batch mode</li>
                        <li>CSV + JSON export</li>
                    </ul>
                    <a href="{{ config.checkout_starter }}" class="plan-btn primary">Get Starter</a>
                </div>
                <div class="plan-card">
                    <div class="plan-name">Pro</div>
                    <div class="plan-price">$4<span>/mo</span></div>
                    <ul class="plan-features">
                        <li>Unlimited transcripts</li>
                        <li>All 1000+ platforms</li>
                        <li>Batch mode</li>
                        <li>CSV + JSON export</li>
                    </ul>
                    <a href="{{ config.checkout_pro }}" class="plan-btn green">Get Pro</a>
                </div>
            </div>
        </div>

        <!-- Login modal -->
        <div class="modal-overlay" id="loginModal" onclick="if(event.target===this)hideLogin()">
            <div class="modal-box">
                <div class="modal-title">Restore your subscription</div>
                <div class="modal-sub">Enter the email you used at checkout</div>
                <input type="email" class="url-input" id="loginEmail" placeholder="you@email.com"
                       onkeydown="if(event.key==='Enter')doLogin()" style="width:100%;margin-top:12px">
                <div class="modal-err" id="loginErr"></div>
                <button class="go-btn" style="width:100%;margin-top:10px" onclick="doLogin()">Restore</button>
            </div>
        </div>

        <div class="footer">TranscriptX — 1000+ platforms. Powered by Groq Whisper. Built by Attention Factory.</div>
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
            const c = document.getElementById('results');
            c.insertAdjacentHTML('afterbegin', `
                <div class="result-card" style="text-align:center;border-color:var(--orange);">
                    <div style="font-size:1.1rem;font-weight:600;margin-bottom:8px;">${msg}</div>
                    <a href="#pricing" style="color:var(--accent-bright);">View plans →</a>
                </div>
            `);
        }

        async function updateCredits() {
            try {
                const r = await fetch('/api/me');
                const u = await r.json();
                document.getElementById('creditBadge').textContent = `${u.plan_name} — ${u.credits_label} credits`;
                document.getElementById('creditBadge').className = `credit-badge ${u.plan}`;
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
                        <div style="color:var(--red);">${d.error||'Unknown error'}</div>
                    </div>`);
                return;
            }
            const id = 'tx-'+Date.now();
            c.insertAdjacentHTML('afterbegin', `
                <div class="result-card">
                    <div class="result-url"><a href="${d.url}" target="_blank">${d.url}</a></div>
                    <div class="stats-grid">
                        <div class="stat"><div class="stat-val">${fmt(d.views)}</div><div class="stat-lbl">Views</div></div>
                        <div class="stat"><div class="stat-val">${fmt(d.likes)}</div><div class="stat-lbl">Likes</div></div>
                        <div class="stat"><div class="stat-val">${fmt(d.comments)}</div><div class="stat-lbl">Comments</div></div>
                        <div class="stat"><div class="stat-val">${d.duration_formatted||'N/A'}</div><div class="stat-lbl">Duration</div></div>
                    </div>
                    <div class="transcript-box">
                        <div class="transcript-head">
                            <span class="transcript-label">Transcript (${d.language||'auto'})</span>
                            <button class="copy-btn" onclick="clip(this,'${id}')">Copy</button>
                        </div>
                        <div class="transcript-text" id="${id}">${d.transcript||'No transcript'}</div>
                    </div>
                </div>`);
        }

        function clip(btn, id) {
            navigator.clipboard.writeText(document.getElementById(id).innerText);
            btn.textContent='Copied!'; btn.classList.add('ok');
            setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('ok');},1500);
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5600))
    debug = os.environ.get("FLASK_ENV") != "production"

    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set! Get one at https://console.groq.com")

    print(f"\n{'='*50}")
    print("⚡ TranscriptX")
    print(f"{'='*50}")
    print(f"\n   http://localhost:{port}\n")

    app.run(debug=debug, host="0.0.0.0", port=port)