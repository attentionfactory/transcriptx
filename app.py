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
import base64
import functools
import hashlib
import hmac
import time
import tempfile
import shutil
from urllib.parse import urlencode
from datetime import datetime, timedelta
from xml.sax.saxutils import escape as _xml_escape

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
from disposable_email_domains import blocklist as _disposable_pkg
from dotenv import load_dotenv

EXTRA_DISPOSABLE_DOMAINS = {
    # Manual additions (general)
    "tempmail.com", "tempmail.io", "tempmail.net",
    "throwaway.email", "burnermail.io", "trashmailr.com",
    "temp-mail.io", "tempemail.cc", "tempemailco.com",
    "tempmailgen.com", "tempinboxmail.com", "tempm.com",
    "temporary.best", "temp.now", "disposablemail.com",
    "5minmail.com", "hour.email", "noemail.cc",
    "anonibox.com", "luxusmail.org", "mail7.app",
    "dmailpro.net", "adresseemailtemporaire.com",
    "emailtemporalgratis.com", "emailtemporanea.org",
    # temp-mail.org network (all resolve to 167.172.0.78)
    "wetuns.com",
    "1800banks.com", "93re.com", "a2qp.com", "abybuy.com", "adeany.com",
    "adventurcraftmx.mx", "affekopf.ch", "aituvip.com", "aixne.com", "akdip.com",
    "allrealfinanz.com", "alysz.com", "american-tall.com", "amozix.com",
    "amzreports.online", "anidaw.com", "anypsd.com", "apostv.com", "arktico.com",
    "auxille.com", "ayfoto.com", "azqas.com", "bachnam.net", "barneu.com",
    "bettereve.com", "bhamweekly.com", "bmoar.com", "boftm.com", "boixi.com",
    "boxnavi.com", "ceberium.com", "cevipsa.com", "chonxi.com", "ckqtlcsvqw.shop",
    "claudecollection.shop", "cnanb.com", "cohdi.com", "coinxt.net", "cosxo.com",
    "cpav3.com", "crowfiles.shop", "daddygo.site", "dbkmail.de", "dietna.com",
    "dotzq.com", "dropcourse.net", "duclongshop.com", "dwseal.com", "e-bazar.org",
    "e052.com", "educart.shop", "effexts.com", "encode-inc.com", "enmaila.com",
    "eosatx.com", "ermael.com", "estateapp.ng", "estebanmx.com", "eveist.com",
    "exuge.com", "fabtivia.com", "fdigimail.web.id", "finloe.com", "flyrine.com",
    "fp-sys.com", "freans.com", "fuddydaddy.com", "gamerx1.linkpc.net",
    "ghostmailz.xyz", "gonaute.com", "govfederal.ca", "haja.me", "hdala.com",
    "heixs.com", "hisila.com", "hkirsan.com", "horsesontour.com", "hotrod.top",
    "hsfm.co.uk", "hunterscafe.com", "idawah.com", "imalias.com", "inmail7.com",
    "inphuocthuy.vn", "internacionalmex.com", "ioea.net", "iphonaticos.com.br",
    "iswire.com", "itcess.com", "jetsay.com", "jmvoice.com", "jokerstash.cc",
    "jqmails.com", "kaedar.com", "kalivo.com.tr", "keokeg.com", "keshavvortex.com",
    "klav6.com", "liaphoto.com", "lifezg.com", "linkrer.com", "lutfyy.shop",
    "lwide.com", "lyunsa.com", "m.e-v.cc", "macosten.com", "magos.dev",
    "mail-data.net", "mail.aarondean.net", "mailfm.net", "mailsd.net", "mailvq.net",
    "mailvs.net", "makemoney15.com", "makemybiz.com", "maltabitcoinmining.com",
    "markoai.my.id", "maxric.com", "maylx.com", "megacode.to", "menitao.com",
    "midimaster.co.kr", "mijn-bedrijf.info", "mitrajagoan.store", "mocvn.com",
    "mofpay.com", "mypethealh.com", "natiret.com", "ncsar.com", "netinta.com",
    "ngem.net", "nhatu.com", "nicloo.com", "novatiz.com", "nuclene.com",
    "numenor.cc", "oazv.net", "octbit.com", "ofirit.com", "onepvp.com",
    "onoranzefunebridegiovine.com", "onymi.com", "outlookua.online",
    "oxbridgecertified.info", "oxtenda.com", "papl-help.store", "parclan.com",
    "pekoi.com", "pmdeal.com", "professorpk.com", "qmailv.com", "rambara.com",
    "reeee.online", "renno.email", "revoadastore.shop", "rhconseiltn.com",
    "roalx.com", "rosebird.org", "roudar.com", "royalvx.com", "saierw.com",
    "saigh5.com.br", "sanzv.com", "scatinc.com", "sdlat.com", "siiii.mywire.org",
    "sixoplus.com", "sixze.com", "soool.online", "spotale.com", "spotshops.com",
    "sskaid.com", "steveix.com", "stoptheyap.com", "student.io.vn", "sunstones.biz",
    "supenc.com", "svmail.publicvm.com", "sweemri.com", "tatefarm.com",
    "tdekeg.online", "techtary.com", "temp.meshari.dev", "tempmail.j78.org",
    "tenvil.com", "tgvis.com", "theamzrfnd.org", "theaumos.com", "thesunand.com",
    "tirillo.com", "tlook.online", "toolve.com", "toymarques.shop", "travile.com",
    "trynta.com", "tunelux.com", "uaxpress.com", "udo8.com", "uncle-jordan.pro",
    "unite5.com", "uptodate.company", "uswaid.com", "venaten.com", "welman.online",
    "whyknapp.com", "wifwise.com", "wikizs.com", "woweix.com", "wyla13.com",
    "xadoll.com", "xlcool.com", "xredb.com", "yakelu.com", "ymhis.com",
    "ypolf.com", "yusolar.com", "zarhq.com", "zealian.com", "zizvy.com",
    "zonnenpanelen.top", "zosce.com",
}
disposable_domains = _disposable_pkg | EXTRA_DISPOSABLE_DOMAINS

# Known IPs of disposable-email mail servers (temp-mail.org network, etc.).
# If a domain's MX record resolves to one of these IPs, it's disposable —
# even if the domain name isn't in any blocklist yet.
_DISPOSABLE_MX_IPS = {
    "167.172.0.78",   # temp-mail.org primary (DigitalOcean, North Bergen NJ)
}


def _is_disposable_mx(domain):
    """Check if a domain's MX record points to a known disposable-mail IP.

    Returns True if disposable, False if clean or if DNS lookup fails
    (we err on the side of allowing the signup rather than blocking on
    transient DNS errors).
    """
    import socket
    try:
        import dns.resolver
        answers = dns.resolver.resolve(domain, "MX")
        for rdata in answers:
            mx_host = str(rdata.exchange).rstrip(".")
            try:
                mx_ip = socket.gethostbyname(mx_host)
                if mx_ip in _DISPOSABLE_MX_IPS:
                    return True
            except socket.gaierror:
                continue
        return False
    except ImportError:
        # dnspython not installed — fall back to just the static list.
        return False
    except Exception:
        return False

load_dotenv()  # Load .env file automatically

import bcrypt
import requests as http_requests
from flask import Flask, request, jsonify, session, redirect, render_template, render_template_string, Response, stream_with_context, send_from_directory, send_file, after_this_request
from database import (
    init_db, PLANS,
    get_free_credits, use_free_credit,
    get_user, get_user_credits, use_user_credit,
    create_user, get_user_by_email, get_user_by_id,
    set_verify_code, verify_email, verify_code_for_user, set_user_password,
    log_transcript_attempt, set_transcript_rating,
    get_transcript_log, mark_transcript_retried,
    maybe_claim_dunning_stage, clear_dunning_stage,
    set_billing_interval,
    get_or_create_referral_code, get_user_by_referral_code,
    set_referred_by, pay_referrer_if_due, get_referral_stats,
    add_bonus_credits, REFERRAL_REWARD_CREDITS,
    get_credits_for_user, use_credit_for_user, refund_credit_for_user,
    grant_credits,
    link_polar_to_user,
    get_banner, set_config,
    claim_webhook_event,
    release_webhook_event,
    sync_polar_subscription_webhook,
    effective_entitlement,
)
from transcribe import process_url, download_video_mp4, clip_video_segment, _sanitize_filename
from routes_pages import register_page_routes
from seo_catalog import current_lastmod, get_platform_pages, get_static_seo_paths

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-" + uuid.uuid4().hex)

# Polar config
POLAR_WEBHOOK_SECRET = os.environ.get("POLAR_WEBHOOK_SECRET", "")
POLAR_STARTER_PRODUCT_ID = os.environ.get("POLAR_STARTER_PRODUCT_ID", "")
POLAR_PRO_PRODUCT_ID = os.environ.get("POLAR_PRO_PRODUCT_ID", "")
POLAR_STARTER_ANNUAL_PRODUCT_ID = os.environ.get("POLAR_STARTER_ANNUAL_PRODUCT_ID", "")
POLAR_PRO_ANNUAL_PRODUCT_ID = os.environ.get("POLAR_PRO_ANNUAL_PRODUCT_ID", "")
POLAR_CHECKOUT_STARTER = os.environ.get("POLAR_CHECKOUT_STARTER", "#")
POLAR_CHECKOUT_PRO = os.environ.get("POLAR_CHECKOUT_PRO", "#")
POLAR_CHECKOUT_STARTER_ANNUAL = os.environ.get("POLAR_CHECKOUT_STARTER_ANNUAL", "").strip() or POLAR_CHECKOUT_STARTER
POLAR_CHECKOUT_PRO_ANNUAL = os.environ.get("POLAR_CHECKOUT_PRO_ANNUAL", "").strip() or POLAR_CHECKOUT_PRO
POLAR_CUSTOMER_PORTAL = os.environ.get("POLAR_CUSTOMER_PORTAL", "#")
# Win-back checkout URLs (with a one-time discount code baked in) emailed to
# users whose subscription was revoked. Fall back to standard checkout when unset.
POLAR_CHECKOUT_WINBACK_STARTER = os.environ.get("POLAR_CHECKOUT_WINBACK_STARTER", "").strip() or POLAR_CHECKOUT_STARTER
POLAR_CHECKOUT_WINBACK_PRO = os.environ.get("POLAR_CHECKOUT_WINBACK_PRO", "").strip() or POLAR_CHECKOUT_PRO
FEATUREBASE_APP_ID = os.environ.get("FEATUREBASE_APP_ID", "")
FEATUREBASE_JWT_SECRET = os.environ.get("FEATUREBASE_JWT_SECRET", "").strip()

# Standard Webhooks (Polar) — timestamp skew tolerance for signature verification
WEBHOOK_TS_TOLERANCE_SEC = 300
_dev_polar_webhook_warned = False

# Supported transcription languages (ISO-639-1). Empty string / None = auto-detect.
# Whisper officially supports 90+ languages; we expose the top 25 by usage plus
# a free-form "other" path that accepts any 2-letter ISO code that matches this regex.
SUPPORTED_LANGUAGES = {
    "en", "es", "fr", "de", "pt", "it", "ja", "ko", "zh", "ru",
    "ar", "hi", "nl", "pl", "tr", "sv", "da", "no", "fi", "cs",
    "uk", "vi", "th", "id", "ms", "he", "ro", "el", "hu", "bg",
    "ca", "fa", "ta", "ur", "bn", "te", "mr", "gu", "kn", "ml",
    "tl", "sw", "af", "sk", "sr", "hr", "lt", "lv", "et", "sl",
}
_LANG_CODE_RE = re.compile(r"^[a-z]{2}$")


def _normalize_language(raw):
    """Validate and normalize a language code. Returns the code or None (auto).

    Empty / missing / 'auto' → None (auto-detect).
    Known code → the code.
    Any other value → raises ValueError so the caller can return 400.
    """
    if raw is None:
        return None
    code = str(raw).strip().lower()
    if code in ("", "auto"):
        return None
    if not _LANG_CODE_RE.match(code):
        raise ValueError("language must be a 2-letter ISO-639-1 code")
    if code not in SUPPORTED_LANGUAGES:
        raise ValueError(f"language '{code}' is not supported")
    return code

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


@app.route("/robots.txt")
def robots_txt():
    return Response("User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\nSitemap: https://transcriptx.xyz/sitemap.xml\nLLMs: https://transcriptx.xyz/llms.txt\n", mimetype="text/plain")


@app.route("/llms.txt")
def llms_txt():
    return send_from_directory(".", "llms.txt", mimetype="text/plain; charset=utf-8")


@app.route("/sitemap.xml")
def sitemap_xml():
    base = "https://transcriptx.xyz"
    lastmod = current_lastmod()
    rows = [
        ("/", "1.0"),
        ("/pricing", "0.8"),
        ("/profile-links", "0.7"),
        ("/guides", "0.7"),
    ]
    rows.extend((path, "0.85") for path in sorted(get_static_seo_paths()))
    rows.extend((f"/guides/{slug}", "0.75") for slug in sorted(GUIDES_CONTENT.keys()))
    rows.extend((f"/platform/{slug}-transcript-generator", "0.7") for slug in sorted(get_platform_pages().keys()))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, priority in rows:
        loc = _xml_escape(f"{base}{path}")
        parts.append(
            f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        )
    parts.append("</urlset>")
    return Response("\n".join(parts), mimetype="application/xml")


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
            current_pwd_marker = user.get("password_changed_at") or ""
            has_session_marker = "pwd_changed_at" in session
            session_pwd_marker = session.get("pwd_changed_at", "")
            if (has_session_marker and session_pwd_marker != current_pwd_marker) or (
                not has_session_marker and current_pwd_marker
            ):
                session.pop("user_id", None)
                session.pop("pwd_changed_at", None)
            else:
                if not has_session_marker:
                    session["pwd_changed_at"] = current_pwd_marker
                    session.modified = True
            ent = effective_entitlement(user)
            eff_plan = ent["effective_plan"]
            plan = PLANS.get(eff_plan, PLANS["free"])
            credits = get_credits_for_user(user_id)
            return {
                "type": "paid" if ent["has_paid_access"] else "authed_free",
                "user_id": user["id"],
                "email": user["email"],
                "plan": eff_plan,
                "plan_name": plan.get("name", eff_plan.title()),
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


def _send_email(to, subject, html):
    """Send a single transactional email via Resend. Returns True on success.

    In dev (no RESEND_API_KEY) this logs the subject to stdout and returns True
    so flows that depend on a successful send keep working locally.
    """
    if not RESEND_API_KEY:
        print(f"⚠️  RESEND_API_KEY not set. Would send to {to}: {subject}")
        return True

    try:
        resp = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Resend error: {e}")
        return False


def _send_otp_email(email, code, purpose="verification"):
    """Send OTP via Resend API. Returns True on success."""
    noun = "password reset" if purpose == "password_reset" else "verification"
    html = f"""
        <div style="font-family:monospace;max-width:400px;margin:0 auto;padding:2rem;">
            <h2 style="margin:0 0 1rem;">TranscriptX</h2>
            <p>Your {noun} code:</p>
            <div style="font-size:2rem;font-weight:bold;letter-spacing:0.3em;padding:1rem;background:#f5f5f5;text-align:center;border-radius:8px;">{code}</div>
            <p style="opacity:0.6;font-size:0.85rem;margin-top:1rem;">This code expires in 10 minutes.</p>
        </div>
    """
    return _send_email(email, f"TranscriptX — Your {noun} code is {code}", html)


def _dunning_html(stage, plan, portal_url, checkout_url):
    """Return (subject, html) for a given dunning stage. Pure — easy to test."""
    if stage == "past_due":
        subject = "TranscriptX — we couldn't charge your card"
        body = f"""
            <div style="font-family:monospace;max-width:480px;margin:0 auto;padding:2rem;">
                <h2 style="margin:0 0 1rem;">Your payment didn't go through</h2>
                <p>We tried to renew your {plan.title()} subscription but your card was declined. You still have access for a few days while we retry — update your payment method to keep things running.</p>
                <p><a href="{portal_url}" style="display:inline-block;padding:.75rem 1.25rem;background:#0a0a0a;color:#F0A860;text-decoration:none;border-radius:6px;font-weight:700;">Update payment method</a></p>
                <p style="opacity:0.6;font-size:0.8rem;margin-top:1.5rem;">If you meant to cancel, you can ignore this email — your plan will end on its own.</p>
            </div>
        """
        return subject, body

    if stage == "canceled":
        subject = "TranscriptX — you'll be missed"
        body = f"""
            <div style="font-family:monospace;max-width:480px;margin:0 auto;padding:2rem;">
                <h2 style="margin:0 0 1rem;">Sorry to see you go</h2>
                <p>Your {plan.title()} subscription is set to end at the close of your current billing period — you'll keep full access until then.</p>
                <p>If something was missing or didn't work as expected, I'd genuinely like to know. Just hit reply.</p>
                <p><a href="{portal_url}" style="display:inline-block;padding:.75rem 1.25rem;background:#0a0a0a;color:#F0A860;text-decoration:none;border-radius:6px;font-weight:700;">Manage subscription</a></p>
            </div>
        """
        return subject, body

    if stage == "revoked":
        subject = "TranscriptX — come back for 50% off"
        body = f"""
            <div style="font-family:monospace;max-width:480px;margin:0 auto;padding:2rem;">
                <h2 style="margin:0 0 1rem;">Want to give it another shot?</h2>
                <p>Your TranscriptX subscription has ended. If you change your mind, here's a 50% discount on your first month back.</p>
                <p><a href="{checkout_url}" style="display:inline-block;padding:.75rem 1.25rem;background:#709472;color:#fff;text-decoration:none;border-radius:6px;font-weight:700;">Resubscribe at 50% off</a></p>
                <p style="opacity:0.6;font-size:0.8rem;margin-top:1.5rem;">This offer is one-time — we won't follow up again.</p>
            </div>
        """
        return subject, body

    return None, None


def _maybe_send_dunning_email(user, stage):
    """Claim a dunning stage and send the matching email if this is a new stage.

    ``user`` is the dict returned by get_user / get_user_by_id. ``stage`` is one of
    'past_due' / 'canceled' / 'revoked'. Safe to call multiple times — guarded by
    maybe_claim_dunning_stage so repeated webhooks only email once.
    """
    if not user or not user.get("email"):
        return False

    user_id = user.get("id")
    if not maybe_claim_dunning_stage(user_id, stage):
        return False

    plan = (user.get("plan") or "starter").lower()
    checkout_url = POLAR_CHECKOUT_WINBACK_PRO if plan == "pro" else POLAR_CHECKOUT_WINBACK_STARTER
    subject, html = _dunning_html(stage, plan, POLAR_CUSTOMER_PORTAL, checkout_url)
    if not subject:
        return False

    return _send_email(user["email"], subject, html)


def _b64url_json(obj):
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _featurebase_jwt_for_user(user):
    """Create HS256 JWT for Featurebase secure Messenger boot."""
    if not FEATUREBASE_JWT_SECRET or not user:
        return None
    email = (user.get("email") or "").strip().lower()
    user_id = str(user.get("id") or "")
    if not email and not user_id:
        return None

    ent = effective_entitlement(user)
    effective_plan = ent.get("effective_plan", "free")
    plan_cfg = PLANS.get(effective_plan, PLANS["free"])
    billing_state = (user.get("billing_state") or "").strip().lower() or "none"

    now = int(time.time())
    payload = {
        "sub": user_id or email,
        "userId": user_id or None,
        "email": email or None,
        "name": (email.split("@")[0] if email else f"user-{user_id}"),
        # Custom attributes (must exist in Featurebase Settings > Attributes).
        "plan": effective_plan,
        "plan_name": plan_cfg.get("name", effective_plan.title()),
        "subscription_status": "paid" if ent.get("has_paid_access") else "free",
        "billing_state": billing_state,
        "iat": now,
        "exp": now + 1800,
    }
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}

    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_b64url_json(header)}.{_b64url_json(payload)}"
    sig = hmac.new(
        FEATUREBASE_JWT_SECRET.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
    return f"{signing_input}.{sig_b64}"


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def _is_production():
    return os.environ.get("FLASK_ENV") == "production"


def _normalize_banner_payload(data):
    payload = data if isinstance(data, dict) else {}
    enabled = bool(payload.get("enabled"))
    text = str(payload.get("text", "")).strip()
    dismissible = bool(payload.get("dismissible", True))

    cta = payload.get("cta")
    if cta is None:
        return {
            "enabled": enabled,
            "text": text,
            "cta": None,
            "dismissible": dismissible,
        }, None

    if not isinstance(cta, dict):
        return None, "CTA must be an object."

    label = str(cta.get("label", "")).strip()
    url = str(cta.get("url", "")).strip()
    style = str(cta.get("style", "primary")).strip().lower()

    if not label or len(label) > 24:
        return None, "CTA label must be 1-24 characters."
    if style not in ("primary", "ghost", "link"):
        return None, "CTA style must be primary, ghost, or link."
    if not url:
        return None, "CTA URL is required when CTA is set."
    if not (url.startswith("/") or url.startswith("https://") or url.startswith("http://")):
        return None, "CTA URL must be https:// or an internal path."
    if url.startswith(("javascript:", "data:")):
        return None, "CTA URL scheme is not allowed."

    return {
        "enabled": enabled,
        "text": text,
        "cta": {"label": label, "url": url, "style": style},
        "dismissible": dismissible,
    }, None


def _client_ip():
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip() or request.remote_addr
    return request.remote_addr or "0.0.0.0"


class _SlidingWindowLimiter:
    def __init__(self):
        self._hits = {}

    def allow(self, key, max_hits, window_sec):
        now = time.monotonic()
        window_start = now - window_sec
        lst = self._hits.setdefault(key, [])
        lst[:] = [t for t in lst if t > window_start]
        if len(lst) >= max_hits:
            return False
        lst.append(now)
        return True


_auth_rate_limiter = _SlidingWindowLimiter()


def rate_limit_auth(max_hits, window_sec):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            key = f"{f.__name__}:{_client_ip()}"
            if not _auth_rate_limiter.allow(key, max_hits, window_sec):
                return jsonify({"status": "error", "error": "Too many requests. Try again later."}), 429
            return f(*args, **kwargs)

        return wrapped

    return decorator


def _decode_whsec_signing_key(secret: str) -> bytes:
    """Standard Webhooks symmetric secret: whsec_ + base64, or raw UTF-8 bytes."""
    s = secret.strip()
    if s.startswith("whsec_"):
        try:
            return base64.b64decode(s[6:])
        except Exception:
            return s.encode("utf-8")
    return s.encode("utf-8")


def _verify_standard_webhook_symmetric(body: bytes, headers, secret: str) -> bool:
    """Verify Standard Webhooks v1 (HMAC-SHA256) signature; constant-time compare per candidate."""
    msg_id = (headers.get("webhook-id") or "").strip()
    ts = (headers.get("webhook-timestamp") or "").strip()
    sig_header = (headers.get("webhook-signature") or "").strip()
    if not msg_id or not ts or not sig_header:
        return False
    try:
        ts_int = int(ts)
    except ValueError:
        return False
    now = int(time.time())
    if abs(now - ts_int) > WEBHOOK_TS_TOLERANCE_SEC:
        return False
    key = _decode_whsec_signing_key(secret)
    signed_content = f"{msg_id}.{ts}.".encode("utf-8") + body
    expected = hmac.new(key, signed_content, hashlib.sha256).digest()
    for part in sig_header.split():
        part = part.strip()
        if not part.startswith("v1,"):
            continue
        try:
            got = base64.b64decode(part[3:])
        except Exception:
            continue
        if len(got) != len(expected):
            continue
        if hmac.compare_digest(expected, got):
            return True
    return False


def _polar_webhook_verify_ok(body: bytes):
    """Returns None if OK, or (response, status_code) on failure."""
    global _dev_polar_webhook_warned
    secret = POLAR_WEBHOOK_SECRET.strip()
    if _is_production():
        if not secret:
            return jsonify({"error": "Webhook not configured"}), 401
        if not _verify_standard_webhook_symmetric(body, request.headers, secret):
            return jsonify({"error": "Invalid signature"}), 401
        return None
    if not secret:
        if not _dev_polar_webhook_warned:
            logging.warning(
                "POLAR_WEBHOOK_SECRET not set; webhook signatures not verified (development only)"
            )
            _dev_polar_webhook_warned = True
        return None
    if not _verify_standard_webhook_symmetric(body, request.headers, secret):
        return jsonify({"error": "Invalid signature"}), 401
    return None


# ── API Routes ──────────────────────────────────────────────

@app.route("/api/extract", methods=["POST"])
def api_extract():
    """Extract transcript from a URL. Deducts 1 credit. Requires auth."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Please sign up or log in to transcribe."}), 401

    data = request.json or {}
    url = data.get("url", "").strip()
    user_id = user.get("user_id")
    email = user.get("email")

    # Optional language override. None = auto-detect (default, current behaviour).
    try:
        language = _normalize_language(data.get("language"))
    except ValueError as e:
        return jsonify({"status": "error", "error": str(e)}), 400

    if not url:
        log_transcript_attempt(user_id, email, url, "error_no_url", credits_used=0)
        return jsonify({"status": "error", "error": "No URL provided"}), 400

    if not url.startswith(("https://", "http://")):
        log_transcript_attempt(user_id, email, url, "error_invalid_url", credits_used=0)
        return jsonify({"status": "error", "error": "Invalid URL. Must start with https://"}), 400

    # Check + deduct credits
    if user["credits"] != -1 and user["credits"] <= 0:
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return jsonify({"status": "error", "error": "No credits remaining. Upgrade your plan!"}), 403
    if not use_credit_for_user(user["user_id"]):
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return jsonify({"status": "error", "error": "No credits remaining."}), 403

    # Process
    model = data.get("model", "whisper-large-v3-turbo")
    if model not in ("whisper-large-v3-turbo", "whisper-large-v3"):
        model = "whisper-large-v3-turbo"

    result = process_url(url, model=model, language=language)
    if result.get("status") == "error":
        # Refund only when the failure is on us (network, Groq, anti-bot, etc.).
        # If the user supplied a private/unsupported/missing video we still
        # spent yt-dlp + Groq cycles on it, so we keep the credit and tell them.
        if result.get("error_kind") == "user_input":
            log_transcript_attempt(
                user_id, email, url, "error_user_input", credits_used=1,
                requested_language=language,
            )
            result["credit_kept"] = True
        else:
            refund_credit_for_user(user["user_id"])
            log_transcript_attempt(
                user_id, email, url, "error", credits_used=0,
                requested_language=language,
            )
    else:
        log_id = log_transcript_attempt(
            user_id, email, url, "success", credits_used=1,
            requested_language=language,
            detected_language=result.get("language"),
        )
        if log_id:
            result["log_id"] = log_id
        # If this user was referred, pay the referrer on their first success.
        # pay_referrer_if_due is idempotent — safe to call on every success.
        try:
            pay_referrer_if_due(user_id)
        except Exception:
            logging.exception("referral payout failed (non-fatal)")
    return jsonify(result)


@app.route("/api/retranscribe", methods=["POST"])
def api_retranscribe():
    """Retry a previously-delivered transcript with a forced language.

    Free (no credit charged), limited to one retry per log_id ever. The caller
    owns the log_id. Used by the "Retry as English" smart recovery flow when
    auto-detect misidentified the language.
    """
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Not authenticated"}), 401

    data = request.json or {}
    log_id = data.get("log_id")
    try:
        log_id = int(log_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "error": "log_id required"}), 400

    try:
        language = _normalize_language(data.get("language"))
    except ValueError as e:
        return jsonify({"status": "error", "error": str(e)}), 400
    if not language:
        # Retry must target a specific language — "auto" again would just repeat
        # the original failure.
        return jsonify({"status": "error", "error": "language required for retry"}), 400

    log = get_transcript_log(log_id, user["user_id"])
    if not log:
        return jsonify({"status": "error", "error": "Not found"}), 403
    if log.get("retried_at"):
        return jsonify({"status": "error", "error": "Already retried"}), 403
    if (log.get("status") or "") != "success":
        return jsonify({"status": "error", "error": "Can only retry successful transcripts"}), 400

    url = log.get("url") or ""
    if not url:
        return jsonify({"status": "error", "error": "Log is missing a URL"}), 400

    # Claim the retry slot up front so concurrent calls can't double-run.
    if not mark_transcript_retried(log_id, user["user_id"]):
        return jsonify({"status": "error", "error": "Already retried"}), 403

    result = process_url(url, language=language)
    if result.get("status") == "error":
        # The retry itself failed — don't refund credits (there were none), but
        # let the caller know. The retry slot stays claimed so we don't loop.
        return jsonify(result), 200

    result["log_id"] = log_id
    result["retried"] = True
    return jsonify(result)


@app.route("/api/rate-transcript", methods=["POST"])
def api_rate_transcript():
    """Record a thumbs-up (1) / thumbs-down (-1) rating for a delivered transcript."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Not authenticated"}), 401

    data = request.json or {}
    log_id = data.get("log_id")
    rating = data.get("rating")
    try:
        log_id = int(log_id)
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "error": "log_id and rating required"}), 400
    if rating not in (1, -1):
        return jsonify({"status": "error", "error": "rating must be 1 or -1"}), 400

    ok = set_transcript_rating(log_id, user["user_id"], rating)
    if not ok:
        return jsonify({"status": "error", "error": "Not found"}), 403
    return jsonify({"status": "ok"})


@app.route("/api/extract-preview", methods=["POST"])
def api_extract_preview():
    """
    Limited unauthenticated preview flow for SEO landing pages.
    Returns a truncated transcript without consuming user credits.
    """
    data = request.json or {}
    url = str(data.get("url", "")).strip()
    if not url:
        return jsonify({"status": "error", "error": "No URL provided"}), 400
    if not url.startswith(("https://", "http://")):
        return jsonify({"status": "error", "error": "Invalid URL. Must start with https://"}), 400

    now = datetime.utcnow()
    reset_at_raw = session.get("preview_reset_at")
    count = int(session.get("preview_count", 0))
    try:
        reset_at = datetime.fromisoformat(reset_at_raw) if reset_at_raw else None
    except Exception:
        reset_at = None
    if not reset_at or reset_at <= now:
        reset_at = now + timedelta(days=1)
        count = 0
    if count >= 1:
        return jsonify({"status": "error", "error": "Preview limit reached. Try again later or log in for full extraction."}), 429

    model = data.get("model", "whisper-large-v3-turbo")
    if model not in ("whisper-large-v3-turbo", "whisper-large-v3"):
        model = "whisper-large-v3-turbo"

    result = process_url(url, model=model)
    if result.get("status") == "error":
        return jsonify(result), 400

    full = str(result.get("transcript", "") or "")
    preview = full[:1200]
    if len(full) > 1200:
        preview += "\n\n[preview truncated]"

    session["preview_count"] = count + 1
    session["preview_reset_at"] = reset_at.isoformat()
    session.modified = True

    return jsonify(
        {
            "status": "success",
            "url": result.get("url", url),
            "title": result.get("title", ""),
            "thumbnail": result.get("thumbnail", ""),
            "language": result.get("language", "unknown"),
            "transcript_preview": preview,
            "preview_char_count": len(preview),
            "full_char_count": len(full),
            "segments_count": len(result.get("segments") or []),
            "words_count": len(result.get("words") or []),
            "preview_only": True,
        }
    )


@app.route("/api/download-video", methods=["POST"])
def api_download_video():
    """Prototype: download full MP4 from URL for logged-in users."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Login required"}), 401

    data = request.json or {}
    url = str(data.get("url", "")).strip()
    title = str(data.get("title", "")).strip()
    if not url.startswith(("https://", "http://")):
        return jsonify({"status": "error", "error": "Invalid URL"}), 400

    tmpdir = tempfile.mkdtemp(prefix="tx_dl_")

    @after_this_request
    def _cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    video_fp, err = download_video_mp4(url, tmpdir)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    base = _sanitize_filename(title or os.path.splitext(os.path.basename(video_fp))[0], "video")
    return send_file(video_fp, as_attachment=True, download_name=f"{base}.mp4", mimetype="video/mp4")


@app.route("/api/download-segment", methods=["POST"])
def api_download_segment():
    """Prototype: download MP4 segment by [start, end] seconds for logged-in users."""
    user = _get_current_user()
    if not user["logged_in"]:
        return jsonify({"status": "error", "error": "Login required"}), 401

    data = request.json or {}
    url = str(data.get("url", "")).strip()
    title = str(data.get("title", "")).strip()
    try:
        start = float(data.get("start", 0))
        end = float(data.get("end", 0))
    except Exception:
        return jsonify({"status": "error", "error": "Invalid start/end values"}), 400

    if not url.startswith(("https://", "http://")):
        return jsonify({"status": "error", "error": "Invalid URL"}), 400
    if start < 0 or end <= start:
        return jsonify({"status": "error", "error": "Invalid segment range"}), 400
    if (end - start) > 1800:
        return jsonify({"status": "error", "error": "Segment too long (max 30 min)"}), 400

    tmpdir = tempfile.mkdtemp(prefix="tx_seg_")

    @after_this_request
    def _cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    src_fp, err = download_video_mp4(url, tmpdir)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    seg_fp = os.path.join(tmpdir, "segment.mp4")
    clip_err = clip_video_segment(src_fp, seg_fp, start, end)
    if clip_err:
        return jsonify({"status": "error", "error": clip_err}), 400

    base = _sanitize_filename(title or os.path.splitext(os.path.basename(src_fp))[0], "segment")
    span = f"{int(start)}-{int(end)}"
    return send_file(seg_fp, as_attachment=True, download_name=f"{base}_{span}.mp4", mimetype="video/mp4")


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


@app.route("/api/me/referral")
def api_me_referral():
    """Current user's referral code + lifetime stats. Requires auth."""
    user = _get_current_user()
    if not user.get("logged_in"):
        return jsonify({"status": "error", "error": "Login required"}), 401
    stats = get_referral_stats(user["user_id"])
    return jsonify({"status": "ok", **stats})


@app.route("/api/featurebase-token")
def api_featurebase_token():
    """Return secure Featurebase JWT for logged-in user."""
    user = _get_current_user()
    if not user.get("logged_in"):
        return jsonify({"status": "error", "error": "Login required"}), 401
    db_user = get_user_by_id(user["user_id"])
    if not db_user:
        return jsonify({"status": "error", "error": "User not found"}), 404
    token = _featurebase_jwt_for_user(db_user)
    if not token:
        return jsonify({"status": "error", "error": "Featurebase JWT unavailable"}), 503
    return jsonify({"status": "ok", "token": token})


# ── Auth Routes ─────────────────────────────────────────────


def _apply_referral_on_signup(new_user_id, new_email, code):
    """Resolve a signup-time referral code. Grants +REFERRAL_REWARD_CREDITS
    to the new user now; the referrer is paid later on the first successful
    transcription (see /api/extract). Safely ignores invalid/self/match codes.
    """
    if not code:
        return None
    referrer = get_user_by_referral_code(code)
    if not referrer:
        return None
    referrer_id = referrer.get("id")
    referrer_email = (referrer.get("email") or "").strip().lower()
    new_email_lc = (new_email or "").strip().lower()

    # Self-referral guard: the new user cannot reuse their own code (not
    # possible on pure signup, but also block email-match in case an
    # unverified account is completing signup).
    if not referrer_id or referrer_id == new_user_id:
        return None
    if new_email_lc and referrer_email and new_email_lc == referrer_email:
        return None

    if set_referred_by(new_user_id, referrer_id):
        add_bonus_credits(new_user_id, REFERRAL_REWARD_CREDITS)
        return referrer_id
    return None


@app.route("/api/signup", methods=["POST"])
@rate_limit_auth(5, 60)
def api_signup():
    """Register with email + password, send OTP."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    referral_code = (data.get("referral_code") or "").strip().upper()

    if not email or not EMAIL_RE.match(email):
        return jsonify({"status": "error", "error": "Valid email required"}), 400
    email_domain = email.split("@")[1]
    if email_domain in disposable_domains or _is_disposable_mx(email_domain):
        return jsonify({"status": "error", "error": "Disposable email addresses are not allowed"}), 400
    if len(password) < 6:
        return jsonify({"status": "error", "error": "Password must be at least 6 characters"}), 400

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing and existing.get("email_verified"):
        return jsonify({"status": "error", "error": "Account already exists. Log in instead."}), 409
    if existing and not existing.get("email_verified"):
        # Re-signup for unverified account — update password + resend code.
        # Also apply referral in case this is their second attempt and they
        # provided a code now. set_referred_by is a no-op if already set.
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        from database import get_db
        with get_db() as db:
            db.execute(
                "UPDATE users SET password_hash = ?, password_changed_at = ? WHERE id = ?",
                (pw_hash, datetime.utcnow().isoformat(), existing["id"]),
            )
        _apply_referral_on_signup(existing["id"], email, referral_code)
        code = _generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        set_verify_code(email, code, expires)
        _send_otp_email(email, code)
        return jsonify({"status": "ok", "step": "verify"})

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = create_user(email, pw_hash)

    if not user_id:
        return jsonify({"status": "error", "error": "Account already exists."}), 409

    _apply_referral_on_signup(user_id, email, referral_code)

    # Generate + send OTP
    code = _generate_otp()
    expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    set_verify_code(email, code, expires)
    _send_otp_email(email, code)

    return jsonify({"status": "ok", "step": "verify"})


@app.route("/api/verify", methods=["POST"])
@rate_limit_auth(15, 60)
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
    session["pwd_changed_at"] = user.get("password_changed_at") or ""
    session.pop("polar_customer_id", None)  # clean up legacy
    return jsonify({"status": "ok"})


@app.route("/api/resend-code", methods=["POST"])
@rate_limit_auth(5, 3600)
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


@app.route("/api/forgot-password/request", methods=["POST"])
@rate_limit_auth(5, 3600)
def api_forgot_password_request():
    """Send password reset OTP if account exists."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    if not email or not EMAIL_RE.match(email):
        return jsonify({"status": "error", "error": "Valid email required"}), 400

    user = get_user_by_email(email)
    if user:
        code = _generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        set_verify_code(email, code, expires)
        _send_otp_email(email, code, purpose="password_reset")

    # Always return success shape to avoid account enumeration.
    return jsonify(
        {
            "status": "ok",
            "message": "If the account exists, a reset code has been sent.",
        }
    )


@app.route("/api/forgot-password/confirm", methods=["POST"])
@rate_limit_auth(10, 3600)
def api_forgot_password_confirm():
    """Reset password using email + OTP code."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()
    new_password = data.get("password", "")

    if not email or not EMAIL_RE.match(email):
        return jsonify({"status": "error", "error": "Valid email required"}), 400
    if len(code) != 6 or not code.isdigit():
        return jsonify({"status": "error", "error": "Valid 6-digit code required"}), 400
    if len(new_password) < 6:
        return jsonify({"status": "error", "error": "Password must be at least 6 characters"}), 400

    user = verify_code_for_user(email, code)
    if not user:
        return jsonify({"status": "error", "error": "Invalid or expired code"}), 400

    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    set_user_password(user["id"], pw_hash)
    session.pop("user_id", None)
    session.pop("pwd_changed_at", None)
    return jsonify({"status": "ok"})


# ── Polar Webhooks ──────────────────────────────────────────

@app.route("/webhooks/polar", methods=["POST"])
def polar_webhook():
    """
    Handle Polar subscription events (Standard Webhooks signed).
    Links polar_customer_id to existing auth'd user by email.
    """
    body = request.get_data(cache=False, as_text=False)

    err = _polar_webhook_verify_ok(body)
    if err is not None:
        return err

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    webhook_id = (request.headers.get("webhook-id") or "").strip()
    if not webhook_id:
        return jsonify({"error": "Missing webhook-id"}), 400

    if not claim_webhook_event(webhook_id):
        return jsonify({"status": "ok", "message": "duplicate"}), 200

    try:
        event_type = data.get("type", "")
        event_data = data.get("data", {})

        product = event_data.get("product") or {}
        product_id = product.get("id") or event_data.get("product_id") or ""
        customer = event_data.get("customer") or {}
        polar_id = customer.get("id") or event_data.get("customer_id") or ""

        plan = None
        billing_interval = None
        if POLAR_PRO_PRODUCT_ID and product_id == POLAR_PRO_PRODUCT_ID:
            plan, billing_interval = "pro", "monthly"
        elif POLAR_STARTER_PRODUCT_ID and product_id == POLAR_STARTER_PRODUCT_ID:
            plan, billing_interval = "starter", "monthly"
        elif POLAR_PRO_ANNUAL_PRODUCT_ID and product_id == POLAR_PRO_ANNUAL_PRODUCT_ID:
            plan, billing_interval = "pro", "annual"
        elif POLAR_STARTER_ANNUAL_PRODUCT_ID and product_id == POLAR_STARTER_ANNUAL_PRODUCT_ID:
            plan, billing_interval = "starter", "annual"

        if plan is None:
            strict_types = (
                "subscription.created",
                "subscription.active",
                "subscription.uncanceled",
            )
            if event_type in strict_types:
                logging.warning(
                    "Polar webhook: unknown or missing product for %s (product_id=%r); ignoring",
                    event_type,
                    product_id,
                )
                return jsonify({"status": "ignored", "reason": "unknown_product"}), 200

            # For lifecycle updates without product details, keep existing paid tier if known.
            existing = get_user(polar_id) if polar_id else None
            existing_plan = (existing or {}).get("plan")
            if existing_plan in ("starter", "pro"):
                plan = existing_plan
            else:
                logging.warning(
                    "Polar webhook: cannot infer plan for %s (product_id=%r, polar_id=%r); ignoring",
                    event_type,
                    product_id,
                    polar_id,
                )
                return jsonify({"status": "ignored", "reason": "unknown_product"}), 200

        subscription_events = (
            "subscription.created",
            "subscription.updated",
            "subscription.active",
            "subscription.canceled",
            "subscription.revoked",
            "subscription.past_due",
            "subscription.uncanceled",
        )
        if event_type in subscription_events:
            sync_polar_subscription_webhook(event_type, event_data, plan)
            if billing_interval and polar_id:
                set_billing_interval(polar_id, billing_interval)
            logging.info(
                "Polar webhook %s synced (plan=%s, interval=%s)",
                event_type,
                plan,
                billing_interval or "unknown",
            )

            # Dunning: fire recovery emails on state transitions. Idempotent —
            # maybe_claim_dunning_stage ensures we only email once per stage.
            # Note: if Polar delivers a canceled/revoked event for a polar_id
            # we've never seen (no prior active/past_due), get_user returns
            # None and no email fires. That's the lesser of two evils —
            # better than creating empty users or double-sending.
            synced_user = get_user(polar_id) if polar_id else None
            if synced_user:
                if event_type == "subscription.past_due":
                    _maybe_send_dunning_email(synced_user, "past_due")
                elif event_type == "subscription.canceled":
                    _maybe_send_dunning_email(synced_user, "canceled")
                elif event_type == "subscription.revoked":
                    _maybe_send_dunning_email(synced_user, "revoked")
                elif event_type in ("subscription.active", "subscription.uncanceled"):
                    # Back to healthy — reset so the next bad event can email.
                    clear_dunning_stage(synced_user.get("id"))

        return jsonify({"status": "ok"}), 200
    except Exception:
        release_webhook_event(webhook_id)
        logging.exception("Polar webhook processing failed")
        return jsonify({"error": "Webhook processing failed"}), 500


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
@rate_limit_auth(15, 60)
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
    session["pwd_changed_at"] = user.get("password_changed_at") or ""
    ent = effective_entitlement(user)
    return jsonify({"status": "ok", "plan": ent["effective_plan"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Clear session."""
    session.pop("user_id", None)
    session.pop("pwd_changed_at", None)
    session.pop("polar_customer_id", None)
    return jsonify({"status": "ok"})


# ── Admin ───────────────────────────────────────────────────

ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]

@app.route("/admin")
def admin():
    """Admin dashboard — protected by login + email allowlist."""
    user = _get_current_user()
    has_admin_email = user["logged_in"] and user.get("email", "").lower() in ADMIN_EMAILS
    if not has_admin_email:
        return "Not found", 404

    from database import get_db
    with get_db() as db:
        users = [dict(r) for r in db.execute(
            """SELECT u.id, u.polar_customer_id, u.email, u.plan, u.credits_used,
                      u.credits_reset_at, u.created_at,
                      ref.email AS referred_by_email
               FROM users u
               LEFT JOIN users ref ON u.referred_by = ref.id
               WHERE u.plan != 'free'
               ORDER BY u.created_at DESC"""
        ).fetchall()]

        free_users = [dict(r) for r in db.execute(
            """SELECT u.id, u.email, u.credits_used, u.credits_reset_at, u.created_at,
                      ref.email AS referred_by_email
               FROM users u
               LEFT JOIN users ref ON u.referred_by = ref.id
               WHERE u.plan = 'free' AND u.email_verified = 1
               ORDER BY u.created_at DESC"""
        ).fetchall()]

        stats = {
            "total_users": db.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1").fetchone()[0],
            "paid_users": db.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'").fetchone()[0],
            "starter": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'starter'").fetchone()[0],
            "pro": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'pro'").fetchone()[0],
            "free_users": db.execute("SELECT COUNT(*) FROM users WHERE plan = 'free' AND email_verified = 1").fetchone()[0],
            "total_free_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM users WHERE plan = 'free'").fetchone()[0],
            "total_paid_transcripts": db.execute("SELECT COALESCE(SUM(credits_used),0) FROM users WHERE plan != 'free'").fetchone()[0],
            "referred_total": db.execute("SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL").fetchone()[0],
            "referral_paid": db.execute("SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL AND referral_credit_paid = 1").fetchone()[0],
        }

        top_referrers = [dict(r) for r in db.execute(
            """SELECT u.id, u.email, u.referral_code,
                      COUNT(r.id) AS referred,
                      SUM(CASE WHEN r.referral_credit_paid = 1 THEN 1 ELSE 0 END) AS paid
               FROM users u
               JOIN users r ON r.referred_by = u.id
               GROUP BY u.id
               ORDER BY referred DESC
               LIMIT 20"""
        ).fetchall()]

    banner = get_banner()
    return render_template_string(
        ADMIN_TEMPLATE,
        users=users,
        free_users=free_users,
        stats=stats,
        banner=banner,
        top_referrers=top_referrers,
    )


@app.route("/admin/credit", methods=["POST"])
def admin_credit():
    user = _get_current_user()
    has_admin_email = user["logged_in"] and user.get("email", "").lower() in ADMIN_EMAILS
    if not has_admin_email:
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json()
    user_id = data.get("user_id")
    amount = int(data.get("amount", 0))
    if not user_id or amount <= 0:
        return jsonify({"error": "bad request"}), 400
    grant_credits(user_id, amount)
    return jsonify({"ok": True})


@app.route("/admin/banner", methods=["POST"])
def admin_banner():
    user = _get_current_user()
    has_admin_email = user["logged_in"] and user.get("email", "").lower() in ADMIN_EMAILS
    if not has_admin_email:
        return "Not found", 404
    data = request.get_json() or {}
    banner_payload, err = _normalize_banner_payload(data)
    if err:
        return jsonify({"status": "error", "error": err}), 400

    set_config("banner_enabled", "1" if banner_payload["enabled"] else "0")
    set_config("banner_text", banner_payload["text"])
    set_config("banner_json", json.dumps(banner_payload))
    return jsonify({"status": "ok"})


@app.route("/admin/logs")
def admin_logs():
    """Transcript extraction logs with filtering + pagination."""
    user = _get_current_user()
    has_admin_email = user["logged_in"] and user.get("email", "").lower() in ADMIN_EMAILS
    if not has_admin_email:
        return "Not found", 404

    try:
        page = max(1, int(request.args.get("page", "1") or "1"))
    except (TypeError, ValueError):
        page = 1
    per_page = 100
    email_q = (request.args.get("email") or "").strip().lower()
    status_q = (request.args.get("status") or "all").strip().lower()
    platform_q = (request.args.get("platform") or "all").strip().lower()

    platform_patterns = {
        "youtube": ["youtube.com", "youtu.be"],
        "tiktok": ["tiktok.com"],
        "instagram": ["instagram.com"],
        "x": ["x.com", "twitter.com"],
        "pinterest": ["pinterest.com"],
        "facebook": ["facebook.com", "fb.watch"],
        "reddit": ["reddit.com", "redd.it"],
        "vimeo": ["vimeo.com"],
    }

    where = []
    params = []
    if email_q:
        where.append("LOWER(COALESCE(l.email, u.email, '')) LIKE ?")
        params.append(f"%{email_q}%")

    if status_q == "success":
        where.append("l.status = 'success'")
    elif status_q == "failed":
        where.append("l.status != 'success'")

    if platform_q in platform_patterns:
        ors = []
        for token in platform_patterns[platform_q]:
            ors.append("LOWER(l.url) LIKE ?")
            params.append(f"%{token}%")
        where.append("(" + " OR ".join(ors) + ")")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    offset = (page - 1) * per_page

    from database import get_db

    with get_db() as db:
        from_sql = (
            "FROM transcript_logs l "
            "LEFT JOIN users u ON u.id = l.user_id OR LOWER(COALESCE(u.email, '')) = LOWER(COALESCE(l.email, ''))"
        )
        total = db.execute(
            f"SELECT COUNT(*) AS c {from_sql} {where_sql}",
            params,
        ).fetchone()["c"]
        rows = [
            dict(r)
            for r in db.execute(
                f"""SELECT l.id, l.user_id, l.email, l.url, l.status, l.credits_used, l.rating,
                           l.requested_language, l.detected_language, l.retried_at, l.created_at,
                           CASE WHEN COALESCE(u.plan, 'free') IN ('starter','pro') THEN COALESCE(u.plan, 'free') ELSE '' END AS plan_pill
                    {from_sql}
                    {where_sql}
                    ORDER BY l.id DESC
                    LIMIT ? OFFSET ?""",
                params + [per_page, offset],
            ).fetchall()
        ]

        rating_row = db.execute(
            """SELECT
                 SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) AS up,
                 SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) AS down,
                 SUM(CASE WHEN rating IS NOT NULL THEN 1 ELSE 0 END) AS rated
               FROM transcript_logs
               WHERE status = 'success'"""
        ).fetchone()
        up_count = int(rating_row["up"] or 0) if rating_row else 0
        down_count = int(rating_row["down"] or 0) if rating_row else 0
        rated_total = int(rating_row["rated"] or 0) if rating_row else 0
        up_pct = round((up_count / rated_total) * 100, 1) if rated_total else None
        rating_summary = {
            "up": up_count,
            "down": down_count,
            "rated": rated_total,
            "up_pct": up_pct,
        }

    def _platform_guess(url):
        u = (url or "").lower()
        if "youtube.com" in u or "youtu.be" in u:
            return "youtube"
        if "tiktok.com" in u:
            return "tiktok"
        if "instagram.com" in u:
            return "instagram"
        if "x.com" in u or "twitter.com" in u:
            return "x"
        if "pinterest.com" in u:
            return "pinterest"
        if "facebook.com" in u or "fb.watch" in u:
            return "facebook"
        if "reddit.com" in u or "redd.it" in u:
            return "reddit"
        if "vimeo.com" in u:
            return "vimeo"
        return "other"

    for row in rows:
        row["platform_guess"] = _platform_guess(row.get("url"))

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)
    has_prev = page > 1
    has_next = page < total_pages

    base_filters = {"email": email_q, "status": status_q, "platform": platform_q}
    prev_qs = urlencode({**base_filters, "page": page - 1})
    next_qs = urlencode({**base_filters, "page": page + 1})

    return render_template(
        "admin_logs.html",
        rows=rows,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        prev_qs=prev_qs,
        next_qs=next_qs,
        filters=base_filters,
        rating_summary=rating_summary,
    )


ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Admin</title>
    <meta name="robots" content="noindex, nofollow">
    <script defer src="https://cloud.umami.is/script.js" data-website-id="ce056448-487b-4006-87df-54954128cff5"></script>
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
            --electricgreen: #9BBA45;
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
            background:var(--grey); border-radius:var(--radius);
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

        /* Kebab menu */
        .actions-cell { position:relative; width:40px; text-align:center; }
        .kebab-wrap { position:relative; display:inline-block; }
        .kebab-btn {
            background:none; border:none; font-size:1.2rem; cursor:pointer;
            padding:4px 8px; border-radius:4px; line-height:1;
        }
        .kebab-btn:hover { background:rgba(0,0,0,0.08); }
        .kebab-menu {
            display:none; position:absolute; right:0; top:100%; z-index:10;
            background:#fff; border:var(--bw) solid rgba(0,0,0,0.12);
            border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,0.1);
            min-width:140px; overflow:hidden;
        }
        .kebab-menu.open { display:block; }
        .kebab-menu button {
            display:block; width:100%; text-align:left; padding:0.6rem 1rem;
            background:none; border:none; font-family:var(--f-tech);
            font-size:0.7rem; cursor:pointer; font-weight:700;
        }
        .kebab-menu button:hover { background:rgba(0,0,0,0.05); }

        /* Modal */
        .modal-overlay {
            position:fixed; inset:0; background:rgba(0,0,0,0.5);
            display:flex; align-items:center; justify-content:center; z-index:100;
        }
        .modal-box {
            background:var(--grey); border-radius:var(--radius); padding:2rem;
            min-width:320px; max-width:400px;
        }
        .modal-title { font-family:var(--f-wide); font-size:0.85rem; text-transform:uppercase; margin-bottom:4px; }
        .modal-sub { font-size:0.7rem; opacity:0.6; margin-bottom:1rem; }
        .modal-input {
            width:100%; padding:0.7rem 1rem; border:var(--bw) solid rgba(0,0,0,0.15);
            border-radius:0.5rem; font-family:var(--f-tech); font-size:0.8rem;
            background:rgba(255,255,255,0.6); margin-bottom:1rem;
        }
        .modal-actions { display:flex; gap:0.5rem; justify-content:flex-end; }
        .modal-cancel {
            background:none; border:var(--bw) solid rgba(0,0,0,0.2); padding:0.5rem 1.2rem;
            border-radius:0.5rem; font-family:var(--f-tech); font-size:0.7rem; cursor:pointer;
        }
        .modal-confirm {
            background:var(--ink); color:var(--grey); border:none; padding:0.5rem 1.2rem;
            border-radius:0.5rem; font-family:var(--f-tech); font-size:0.7rem;
            font-weight:700; text-transform:uppercase; cursor:pointer;
        }

        /* ── Pagination ── */
        .pagination {
            display:flex; align-items:center; justify-content:center; gap:0.4rem;
            padding:1rem 0; font-family:var(--f-tech); font-size:0.7rem;
        }
        .pg-btn {
            background:var(--grey); border:var(--bw) solid rgba(0,0,0,0.15); padding:0.4rem 0.8rem;
            border-radius:0.4rem; font-family:var(--f-tech); font-size:0.65rem; font-weight:700;
            cursor:pointer; text-transform:uppercase;
        }
        .pg-btn:hover { background:rgba(0,0,0,0.05); }
        .pg-btn:disabled { opacity:0.3; cursor:not-allowed; }
        .pg-btn.active { background:var(--ink); color:var(--grey); border-color:var(--ink); }
        .pg-info { font-size:0.65rem; opacity:0.5; margin:0 0.5rem; }
        .pg-select {
            margin-left:0.8rem; padding:0.4rem 0.6rem; border:var(--bw) solid rgba(0,0,0,0.15);
            border-radius:0.4rem; font-family:var(--f-tech); font-size:0.65rem; font-weight:700;
            background:var(--grey); cursor:pointer;
        }

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
                <a href="/admin/logs">Logs</a>
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
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.referred_total }}">0</div>
                <div class="stat-lbl">Referred Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" data-count="{{ stats.referral_paid }}">0</div>
                <div class="stat-lbl">Referral Payouts</div>
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
            <div class="section-count">{{ stats.paid_users }}</div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr><th>Email</th><th>Plan</th><th>Referred By</th><th>Usage</th><th>Since</th><th></th></tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td class="email-cell">{{ u.email or '—' }}</td>
                        <td><span class="badge {{ u.plan }}">{{ u.plan }}</span></td>
                        <td class="mono">{{ u.referred_by_email or '—' }}</td>
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
                        <td class="actions-cell">
                            <div class="kebab-wrap">
                                <button class="kebab-btn" onclick="toggleMenu(this)">⋮</button>
                                <div class="kebab-menu">
                                    <button onclick="openCreditModal({{ u.id }}, '{{ u.email }}')">Add Credits</button>
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                    {% if not users %}<tr><td colspan="6" class="empty-row">No users yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>

        <!-- Free Users -->
        <div class="section-head">
            <div class="section-title">Free Users</div>
            <div class="section-count">{{ stats.free_users }}</div>
        </div>
        <div class="table-wrap">
            <table id="freeTable">
                <thead>
                    <tr><th>Email</th><th>Referred By</th><th>Usage</th><th>Resets</th><th>Joined</th><th></th></tr>
                </thead>
                <tbody id="freeBody">
                    {% for u in free_users %}
                    <tr>
                        <td class="email-cell">{{ u.email or '—' }}</td>
                        <td class="mono">{{ u.referred_by_email or '—' }}</td>
                        <td>
                            <div class="usage-bar-wrap">
                                <span class="mono">{{ u.credits_used }}</span>
                                <div class="usage-bar"><div class="usage-bar-fill orange" style="width:{{ (u.credits_used / 3 * 100) | int }}%"></div></div>
                                <span class="mono">/ 3</span>
                            </div>
                        </td>
                        <td class="mono">{{ u.credits_reset_at[:10] if u.credits_reset_at else '—' }}</td>
                        <td class="mono">{{ u.created_at[:10] if u.created_at else '—' }}</td>
                        <td class="actions-cell">
                            <div class="kebab-wrap">
                                <button class="kebab-btn" onclick="toggleMenu(this)">⋮</button>
                                <div class="kebab-menu">
                                    <button onclick="openCreditModal({{ u.id }}, '{{ u.email }}')">Add Credits</button>
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                    {% if not free_users %}<tr><td colspan="6" class="empty-row">No free users yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>
        <div class="pagination" id="freePagination"></div>

        <!-- Top Referrers -->
        <div class="section-head">
            <div class="section-title">Top Referrers</div>
            <div class="section-count">{{ top_referrers | length }}</div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr><th>Email</th><th>Code</th><th>Referred</th><th>Paid Out</th><th>Credits Earned</th></tr>
                </thead>
                <tbody>
                    {% for r in top_referrers %}
                    <tr>
                        <td class="email-cell">{{ r.email or '—' }}</td>
                        <td class="mono">{{ r.referral_code or '—' }}</td>
                        <td class="mono">{{ r.referred }}</td>
                        <td class="mono">{{ r.paid }}</td>
                        <td class="mono">{{ (r.paid or 0) * 10 }}</td>
                    </tr>
                    {% endfor %}
                    {% if not top_referrers %}<tr><td colspan="5" class="empty-row">No referrals yet</td></tr>{% endif %}
                </tbody>
            </table>
        </div>

        <!-- Banner Control -->
        <div class="section-head">
            <div class="section-title">Site Banner</div>
        </div>
        <div class="panel" style="background:var(--grey); display:flex; flex-direction:column; gap:1rem;">
            <div style="display:flex; align-items:center; gap:1rem;">
                <label style="font-size:0.7rem; font-weight:700; text-transform:uppercase;">Enabled</label>
                <input type="checkbox" id="bannerEnabled" {% if banner.enabled %}checked{% endif %} style="width:18px; height:18px; cursor:pointer;">
            </div>
            <div style="display:flex; align-items:center; gap:1rem;">
                <label style="font-size:0.7rem; font-weight:700; text-transform:uppercase;">Dismissible</label>
                <input type="checkbox" id="bannerDismissible" {% if banner.dismissible %}checked{% endif %} style="width:18px; height:18px; cursor:pointer;">
            </div>
            <input type="text" id="bannerText" value="{{ banner.text }}" placeholder="Banner message..." style="width:100%; padding:0.8rem 1rem; border:var(--bw) solid rgba(0,0,0,0.15); border-radius:0.5rem; font-family:var(--f-tech); font-size:0.75rem; background:rgba(255,255,255,0.6);">
            <div style="display:flex; align-items:center; gap:1rem;">
                <label style="font-size:0.7rem; font-weight:700; text-transform:uppercase;">CTA</label>
                <input type="checkbox" id="bannerCtaEnabled" {% if banner.cta %}checked{% endif %} style="width:18px; height:18px; cursor:pointer;">
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 170px; gap:0.6rem;">
                <input type="text" id="bannerCtaLabel" value="{{ banner.cta.label if banner.cta else '' }}" placeholder="CTA label (max 24)" style="width:100%; padding:0.8rem 1rem; border:var(--bw) solid rgba(0,0,0,0.15); border-radius:0.5rem; font-family:var(--f-tech); font-size:0.75rem; background:rgba(255,255,255,0.6);">
                <input type="text" id="bannerCtaUrl" value="{{ banner.cta.url if banner.cta else '' }}" placeholder="https://... or /path" style="width:100%; padding:0.8rem 1rem; border:var(--bw) solid rgba(0,0,0,0.15); border-radius:0.5rem; font-family:var(--f-tech); font-size:0.75rem; background:rgba(255,255,255,0.6);">
                <select id="bannerCtaStyle" style="width:100%; padding:0.8rem 1rem; border:var(--bw) solid rgba(0,0,0,0.15); border-radius:0.5rem; font-family:var(--f-tech); font-size:0.75rem; background:rgba(255,255,255,0.6);">
                    <option value="primary" {% if banner.cta and banner.cta.style == 'primary' %}selected{% endif %}>primary</option>
                    <option value="ghost" {% if banner.cta and banner.cta.style == 'ghost' %}selected{% endif %}>ghost</option>
                    <option value="link" {% if banner.cta and banner.cta.style == 'link' %}selected{% endif %}>link</option>
                </select>
            </div>
            <button onclick="saveBanner()" style="align-self:flex-start; background:var(--ink); color:var(--grey); border:none; padding:0.6rem 1.5rem; border-radius:0.5rem; font-family:var(--f-tech); font-size:0.7rem; font-weight:700; text-transform:uppercase; cursor:pointer;">Save Banner</button>
            <div id="bannerStatus" style="font-size:0.7rem; opacity:0.6;"></div>
        </div>

        <!-- Credit Modal -->
        <div id="creditModal" class="modal-overlay" style="display:none;">
            <div class="modal-box">
                <div class="modal-title">Add Credits</div>
                <div class="modal-sub" id="modalUser"></div>
                <input type="number" id="creditAmount" min="1" value="5" placeholder="Credits to add" class="modal-input">
                <div class="modal-actions">
                    <button class="modal-cancel" onclick="closeCreditModal()">Cancel</button>
                    <button class="modal-confirm" onclick="submitCredits()">Grant</button>
                </div>
                <div id="creditStatus" style="font-size:0.7rem; margin-top:0.5rem; opacity:0.6;"></div>
            </div>
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

        async function saveBanner() {
            const enabled = document.getElementById('bannerEnabled').checked;
            const text = document.getElementById('bannerText').value;
            const dismissible = document.getElementById('bannerDismissible').checked;
            const ctaEnabled = document.getElementById('bannerCtaEnabled').checked;
            const ctaLabel = document.getElementById('bannerCtaLabel').value.trim();
            const ctaUrl = document.getElementById('bannerCtaUrl').value.trim();
            const ctaStyle = document.getElementById('bannerCtaStyle').value;
            const st = document.getElementById('bannerStatus');
            const payload = {enabled, text, dismissible, cta: null};
            if (ctaEnabled) {
                payload.cta = {label: ctaLabel, url: ctaUrl, style: ctaStyle};
            }
            try {
                const r = await fetch('/admin/banner', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if (r.ok) {
                    st.textContent = 'Saved!';
                } else {
                    const d = await r.json().catch(() => ({}));
                    st.textContent = d.error || 'Error saving';
                }
                setTimeout(() => st.textContent = '', 2000);
            } catch(e) { st.textContent = 'Error: ' + e.message; }
        }

        let currentUserId = null;

        function toggleMenu(btn) {
            document.querySelectorAll('.kebab-menu.open').forEach(m => m.classList.remove('open'));
            btn.nextElementSibling.classList.toggle('open');
        }

        document.addEventListener('click', e => {
            if (!e.target.closest('.kebab-wrap'))
                document.querySelectorAll('.kebab-menu.open').forEach(m => m.classList.remove('open'));
        });

        function openCreditModal(userId, email) {
            currentUserId = userId;
            document.getElementById('modalUser').textContent = email;
            document.getElementById('creditAmount').value = 5;
            document.getElementById('creditStatus').textContent = '';
            document.getElementById('creditModal').style.display = 'flex';
            document.querySelectorAll('.kebab-menu.open').forEach(m => m.classList.remove('open'));
        }

        function closeCreditModal() {
            document.getElementById('creditModal').style.display = 'none';
            currentUserId = null;
        }

        document.getElementById('creditModal').addEventListener('click', e => {
            if (e.target === e.currentTarget) closeCreditModal();
        });

        async function submitCredits() {
            const amount = parseInt(document.getElementById('creditAmount').value);
            const st = document.getElementById('creditStatus');
            if (!amount || amount <= 0) { st.textContent = 'Enter a valid number'; return; }
            try {
                const r = await fetch('/admin/credit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUserId, amount})
                });
                if (r.ok) {
                    st.textContent = 'Granted ' + amount + ' credits!';
                    setTimeout(() => location.reload(), 800);
                } else {
                    st.textContent = 'Error granting credits';
                }
            } catch(e) { st.textContent = 'Error: ' + e.message; }
        }

        (function() {
            let perPage = 25;
            const tbody = document.getElementById('freeBody');
            const pag = document.getElementById('freePagination');
            if (!tbody || !pag) return;
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const total = rows.length;
            if (total <= 10) return;
            let cur = 1;

            function render() {
                const pages = Math.ceil(total / perPage);
                if (cur > pages) cur = pages;
                const start = (cur - 1) * perPage;
                rows.forEach((r, i) => r.style.display = (i >= start && i < start + perPage) ? '' : 'none');
                pag.innerHTML = '';
                const prev = Object.assign(document.createElement('button'), {textContent: '← Prev', className: 'pg-btn', disabled: cur === 1});
                prev.onclick = () => { cur--; render(); };
                pag.appendChild(prev);
                const info = Object.assign(document.createElement('span'), {textContent: cur + ' / ' + pages, className: 'pg-info'});
                pag.appendChild(info);
                const next = Object.assign(document.createElement('button'), {textContent: 'Next →', className: 'pg-btn', disabled: cur === pages});
                next.onclick = () => { cur++; render(); };
                pag.appendChild(next);
                const sel = document.createElement('select');
                sel.className = 'pg-select';
                [10, 25, 50, 100].forEach(n => {
                    const opt = document.createElement('option');
                    opt.value = n; opt.textContent = n + ' / page';
                    if (n === perPage) opt.selected = true;
                    sel.appendChild(opt);
                });
                sel.onchange = () => { perPage = parseInt(sel.value); cur = 1; render(); };
                pag.appendChild(sel);
            }
            render();
        })();
    </script>
</body>
</html>
"""


# ── UI ──────────────────────────────────────────────────────

GUIDES_CONTENT = {
    "repurpose-video-into-seo-post": {
        "title": "Repurpose Video Content Into SEO Posts (Using TranscriptX)",
        "description": "Use TranscriptX to extract a transcript, edit it into an article, and publish SEO-ready content with a repeatable workflow.",
        "keywords": "repurpose video content, video to blog post, transcript to article, content repurposing workflow",
        "h1": "Repurpose Video Content Into SEO Posts (Using TranscriptX)",
        "quick_answer": "Use TranscriptX to pull a transcript from your video URL, edit it into a clean article structure, optimize for one keyword, and publish.",
        "faq": [
            {
                "q": "Can I publish the raw transcript directly?",
                "a": "You can, but an edited transcript performs better for readability and SEO."
            },
            {
                "q": "How long should the repurposed post be?",
                "a": "Typically 800 to 1500 words, depending on query intent and topic depth."
            },
            {
                "q": "Should one video become one article?",
                "a": "Start with one article, then split high-value videos into multiple intent-specific posts."
            },
            {
                "q": "What if the transcript has minor errors?",
                "a": "Do a fast editorial pass for names, technical terms, and context before publishing."
            },
        ],
        "body_html": """
<p>If you already publish videos, you are sitting on SEO content. The fastest workflow is simple: get transcript, edit into article, publish.</p>
<h2>Quick answer</h2>
<p>Use TranscriptX to pull a transcript from your video URL, clean the text into an article structure, optimize for one keyword, and publish.</p>
<h2>Step-by-step workflow</h2>
<h3>1) Get the transcript with TranscriptX</h3>
<ul>
  <li>Paste your video URL into TranscriptX.</li>
  <li>Run transcription and copy the transcript output.</li>
</ul>
<h3>2) Clean the transcript</h3>
<ul>
  <li>Remove filler words and repeated phrases.</li>
  <li>Split long blocks into short readable sections.</li>
</ul>
<h3>3) Turn transcript into article structure</h3>
<ul>
  <li>Intro with problem + promise</li>
  <li>Quick answer</li>
  <li>Steps/checklist</li>
  <li>Common mistakes</li>
  <li>FAQ + CTA</li>
</ul>
<h3>4) Optimize for SEO before publishing</h3>
<ul>
  <li>Put keyword in title, H1, slug, and first paragraph.</li>
  <li>Add internal links to <a href="/">home</a>, <a href="/pricing">pricing</a>, and <a href="/guides/manual-vs-ai-transcription">manual vs AI</a>.</li>
  <li>Include FAQ for long-tail capture.</li>
</ul>
<h3>5) Publish and interlink</h3>
<ul>
  <li>Publish the page and link related guides to it.</li>
  <li>Submit updated sitemap in Search Console.</li>
</ul>
<h2>Why this works</h2>
<p>Transcript-first writing increases speed and consistency. Every published video becomes a new ranking attempt.</p>
<h2>Common mistakes to avoid</h2>
<ul>
  <li>Publishing raw transcript without editing</li>
  <li>Targeting multiple unrelated keywords on one page</li>
  <li>Skipping FAQ and internal links</li>
  <li>No clear CTA</li>
</ul>
<h2>FAQ</h2>
<h3>Can I publish the raw transcript directly?</h3>
<p>You can, but an edited transcript performs better for readability and SEO.</p>
<h3>How long should the repurposed post be?</h3>
<p>Typically 800 to 1500 words, depending on query intent and topic depth.</p>
<h3>Should one video become one article?</h3>
<p>Start with one article, then split high-value videos into multiple intent-specific posts.</p>
<h3>What if the transcript has minor errors?</h3>
<p>Do a fast editorial pass for names, technical terms, and context before publishing.</p>
<h2>Final take</h2>
<p>Treat TranscriptX as your repurposing engine: every video should become a search-optimized page.</p>
""",
    },
    "manual-vs-ai-transcription": {
        "title": "Stop Typing Manually \u2014 Why Fast Teams Use AI Transcription",
        "description": "Manual transcription costs you time and publishing speed. See why teams are switching to AI-powered transcription with TranscriptX.",
        "keywords": "manual transcription vs ai transcription, ai transcription tool, transcription workflow, transcriptx guide",
        "h1": "Stop Typing Manually \u2014 Why Fast Teams Use AI Transcription",
        "quick_answer": "AI transcription with TranscriptX turns hours of manual typing into minutes of clean, editable text \u2014 so your team publishes faster without losing quality.",
        "faq": [
            {
                "q": "Is AI transcription accurate enough to publish?",
                "a": "Yes. For clear audio, TranscriptX produces highly accurate output. A quick editorial pass handles the rest."
            },
            {
                "q": "When does manual transcription still make sense?",
                "a": "Strict legal or compliance recordings where every syllable matters and volume is low."
            },
            {
                "q": "Will AI transcription make my content sound robotic?",
                "a": "No. TranscriptX produces the draft. Your team controls tone, voice, and final quality."
            },
            {
                "q": "How much faster is AI transcription than manual?",
                "a": "Most videos are transcribed in minutes instead of hours. Editing adds a short pass on top."
            },
            {
                "q": "What does TranscriptX cost compared to hiring a transcriptionist?",
                "a": "TranscriptX starts at $2/month for 50 transcripts. A single freelance transcript can cost $20-50+."
            },
        ],
        "body_html": """
<p>There was a time when transcription meant headphones, a foot pedal, and hours of rewind-type-rewind. For some teams, that is still the default. But the math has changed dramatically, and teams that have not caught up are losing publishing speed every week.</p>

<p>Manual transcription is not bad work. It is thorough, controllable, and precise when done well. The problem is throughput. A skilled typist working from audio needs roughly four hours to transcribe one hour of speech. That means a single 20-minute video eats nearly 90 minutes of focused human effort before a single word is edited, structured, or published. Multiply that by a weekly publishing cadence and you have a full-time bottleneck disguised as a routine task.</p>

<p>AI transcription does not eliminate humans from the process. It changes where humans spend their time. Instead of converting sound to words, your team spends time on structure, voice, and intent \u2014 the parts that actually determine whether content performs. TranscriptX handles the conversion layer: paste a URL, get a clean transcript, then shape it into whatever you need.</p>

<h2>The real cost of manual transcription</h2>

<p>Cost is not just money. It is time, opportunity, and consistency. Manual transcription introduces three hidden costs that most teams underestimate.</p>

<p>First, there is the calendar cost. Every hour spent typing is an hour not spent writing, editing, or distributing. Teams with manual workflows publish less frequently, which means fewer pages indexed, fewer ranking opportunities, and slower compounding growth.</p>

<p>Second, there is the consistency cost. Manual work is subject to energy, availability, and human variability. Miss one week and your publishing rhythm breaks. Miss three and your content pipeline stalls. AI transcription runs on demand regardless of team capacity.</p>

<p>Third, there is the scaling cost. Manual transcription does not scale linearly. Doubling your video output means doubling transcription labor. With AI, doubling video output means doubling API calls \u2014 no new hires, no new processes.</p>

<h2>What AI transcription actually delivers</h2>

<p>Modern speech-recognition engines are trained on hundreds of thousands of hours of diverse, multilingual audio from the real web \u2014 not clean studio recordings. That training breadth is why they handle accents, background noise, and overlapping speech far better than earlier systems. The practical result: you get a usable first draft from imperfect real-world recordings, not just laboratory audio.</p>

<p>TranscriptX uses this technology to give you transcript output in minutes. The workflow is simple: paste the video URL, TranscriptX extracts audio and runs transcription, and you get structured text ready for editing. No file management, no software installs, no waiting for freelancers.</p>

<h2>When manual still wins</h2>

<p>There are legitimate cases where manual transcription is the right call. Legal depositions, compliance-heavy recordings, and highly specialized technical content with dense jargon sometimes need human attention from the first word. If your volume is low and precision requirements are unusually strict, manual work can still justify itself.</p>

<p>But those cases are narrow. For creators, marketers, agencies, and product teams producing content regularly, AI transcription is not just faster \u2014 it is the only way to maintain a sustainable publishing pace without burning out your team.</p>

<h2>How TranscriptX fits your workflow</h2>

<p>TranscriptX is designed for teams that need to move from video to published content quickly. Here is how it works in practice:</p>

<p>You paste a video URL from YouTube, TikTok, Instagram, or any of 1000+ supported sources. TranscriptX extracts the audio automatically \u2014 no downloads, no file conversions on your end. The audio runs through high-accuracy AI transcription and you receive clean, structured text output within minutes.</p>

<p>From there, your team does what humans do best: edit for tone, restructure for the target format, and publish. The entire cycle \u2014 from video URL to published page \u2014 can happen in a single sitting instead of spanning days.</p>

<h2>The publishing speed advantage</h2>

<p>Content that ships weekly compounds faster than content that ships monthly. That is not theory \u2014 it is how search indexing and topical authority work. Every published page is a new entry point, a new ranking opportunity, and a new internal linking node. Teams that transcribe faster, publish faster. Teams that publish faster, grow faster.</p>

<p>TranscriptX exists to remove the bottleneck between having content and publishing content. Your videos already contain the substance. TranscriptX turns that substance into text you can use today.</p>

<h2>FAQ</h2>
<h3>Is AI transcription accurate enough to publish?</h3>
<p>Yes. For clear audio, TranscriptX produces highly accurate output. A quick editorial pass handles the rest.</p>
<h3>When does manual transcription still make sense?</h3>
<p>Strict legal or compliance recordings where every syllable matters and volume is low.</p>
<h3>Will AI transcription make my content sound robotic?</h3>
<p>No. TranscriptX produces the draft. Your team controls tone, voice, and final quality.</p>
<h3>How much faster is AI transcription than manual?</h3>
<p>Most videos are transcribed in minutes instead of hours. Editing adds a short pass on top.</p>
<h3>What does TranscriptX cost compared to hiring a transcriptionist?</h3>
<p>TranscriptX starts at $2/month for 50 transcripts. A single freelance transcript can cost $20\u201350+.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Ready to stop typing and start publishing?</strong></p>
  <a href="/pricing" style="color:#F0A860;font-weight:700;">See TranscriptX pricing \u2192</a>
</div>
""",
    },
    "youtube-transcript-generator": {
        "title": "YouTube Transcript Generator \u2014 Get Clean Text From Any Video",
        "description": "TranscriptX turns any YouTube video into clean, editable transcript text in minutes. Accurate AI transcription you can publish, repurpose, and share.",
        "keywords": "youtube transcript generator, youtube transcript, transcript youtube, youtube to transcript",
        "h1": "YouTube Transcript Generator \u2014 Clean Text From Any Video in Minutes",
        "quick_answer": "Paste a YouTube URL into TranscriptX and get an accurate, editable transcript in minutes \u2014 ready to publish, repurpose, or share.",
        "faq": [
            {
                "q": "How does the TranscriptX YouTube transcript generator work?",
                "a": "Paste a YouTube URL, TranscriptX extracts the audio and runs AI transcription, then returns clean editable text."
            },
            {
                "q": "Is this more accurate than YouTube auto-captions?",
                "a": "TranscriptX uses advanced our AI engine that handles noise, accents, and overlapping speech better than standard auto-captions."
            },
            {
                "q": "Can I use the transcript for blog posts and articles?",
                "a": "Yes. TranscriptX output is designed to be edited and published as articles, guides, social posts, and more."
            },
            {
                "q": "What if a YouTube video has no captions?",
                "a": "TranscriptX does not depend on existing captions. It extracts audio and transcribes directly, so missing captions are not a problem."
            },
            {
                "q": "How much does it cost?",
                "a": "Free users get 3 transcripts per month. Starter is $2/month for 50 transcripts. Pro is $4/month for unlimited."
            },
            {
                "q": "Does it work with long YouTube videos?",
                "a": "Yes, TranscriptX handles videos up to the audio size limit. Most standard YouTube content processes without issues."
            },
        ],
        "body_html": """
<p>Every day, millions of hours of valuable spoken content go live on YouTube. Tutorials, interviews, lectures, product reviews, earnings calls, podcasts \u2014 all of it locked inside video. If you need that content as text, your options have historically been limited: copy-paste from inconsistent auto-captions, hire a transcriptionist, or type it yourself.</p>

<p>TranscriptX changes that equation. Paste a YouTube URL and get a clean, accurate transcript in minutes. Not a rough caption dump \u2014 actual structured text you can edit, publish, and repurpose immediately.</p>

<h2>Why YouTube auto-captions are not enough</h2>

<p>YouTube generates automatic captions using its own speech recognition, and for casual viewing they work reasonably well. But anyone who has tried to use auto-captions as source material for writing knows the frustration. Missing punctuation. Sentence boundaries that make no sense. Names and technical terms mangled beyond recognition. Background noise interpreted as speech.</p>

<p>YouTube\u2019s own documentation acknowledges that automatic captions can vary in quality depending on mispronunciations, accents, dialects, and background noise. For quick reference while watching a video, that is fine. For content production, it creates more editing work than it saves.</p>

<p>Worse, not every video even has captions available. If the creator disabled them, or if the audio conditions prevented auto-generation, the built-in transcript view simply does not appear. You are left with nothing.</p>

<h2>How TranscriptX works</h2>

<p>TranscriptX does not depend on YouTube\u2019s existing caption track. Instead, it extracts the actual audio from the video and runs it through advanced AI speech recognition built on our transcription engine \u2014 trained on hundreds of thousands of hours of diverse, multilingual web audio.</p>

<p>The practical difference is significant. our transcription engine handles real-world audio conditions \u2014 background noise, varied accents, technical vocabulary, multiple languages \u2014 with substantially better accuracy than standard auto-caption systems. Research shows these engines make up to 50% fewer errors than models tuned for narrow benchmark conditions.</p>

<p>Here is the workflow:</p>

<p><strong>Step 1:</strong> Paste the YouTube video URL into TranscriptX.</p>
<p><strong>Step 2:</strong> TranscriptX automatically extracts the audio. No downloads or file management on your end.</p>
<p><strong>Step 3:</strong> AI transcription runs and returns clean, structured text \u2014 typically within minutes.</p>
<p><strong>Step 4:</strong> Copy the transcript, edit it for your needs, and publish.</p>

<p>That is the complete workflow. No software to install, no accounts to configure with third-party APIs, no audio files to juggle.</p>

<h2>What you can do with the transcript</h2>

<p>A clean transcript is not just text \u2014 it is a content asset with multiple downstream uses.</p>

<p><strong>Blog posts and articles.</strong> One 15-minute video contains enough material for a 1,500-word article. Structure the transcript into sections, add an intro and conclusion, and you have a publishable page targeting search traffic you would never capture with video alone.</p>

<p><strong>Social media content.</strong> Pull the strongest quotes, insights, or data points from the transcript. Each one becomes a standalone post, a thread, or a carousel slide. One video can fuel a week of social content.</p>

<p><strong>Documentation and knowledge bases.</strong> Product demos, onboarding sessions, and internal presentations all become searchable reference material once transcribed. Teams stop asking \u201cwhat did we say in that meeting?\u201d and start finding answers instantly.</p>

<p><strong>Accessibility.</strong> Transcripts make your content available to people who are deaf or hard of hearing, people who prefer reading, and people in environments where audio is not practical. Accessibility is not a feature \u2014 it is a responsibility.</p>

<h2>Built for reliability, not just speed</h2>

<p>Speed matters, but not if the tool breaks every other attempt. YouTube periodically changes how it serves content, and extraction tools that do not adapt fail silently. TranscriptX includes automatic retry logic, intelligent fallback handling, and clear error messaging when something upstream changes. You get a result or you get an honest explanation \u2014 never a blank screen.</p>

<p>This operational resilience is invisible when everything works, but it is the difference between a tool you use once and a tool your team relies on weekly.</p>

<h2>Pricing that makes sense</h2>

<p>TranscriptX is built for creators and teams, not enterprise budgets. Free users get 3 transcripts per month with no signup. Starter gives you 50 transcripts for $2/month. Pro gives you unlimited for $4/month. Compare that to transcription services charging $1\u2013$2 per minute of audio, and the economics are not even close.</p>

<h2>FAQ</h2>
<h3>How does the TranscriptX YouTube transcript generator work?</h3>
<p>Paste a YouTube URL, TranscriptX extracts the audio and runs AI transcription, then returns clean editable text.</p>
<h3>Is this more accurate than YouTube auto-captions?</h3>
<p>TranscriptX uses advanced our AI engine that handles noise, accents, and overlapping speech better than standard auto-captions.</p>
<h3>Can I use the transcript for blog posts and articles?</h3>
<p>Yes. TranscriptX output is designed to be edited and published as articles, guides, social posts, and more.</p>
<h3>What if a YouTube video has no captions?</h3>
<p>TranscriptX does not depend on existing captions. It extracts audio and transcribes directly, so missing captions are not a problem.</p>
<h3>How much does it cost?</h3>
<p>Free users get 3 transcripts per month. Starter is $2/month for 50 transcripts. Pro is $4/month for unlimited.</p>
<h3>Does it work with long YouTube videos?</h3>
<p>Yes, TranscriptX handles videos up to the audio size limit. Most standard YouTube content processes without issues.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Ready to turn YouTube videos into publishable text?</strong></p>
  <a href="/" style="color:#F0A860;font-weight:700;">Try TranscriptX free \u2192</a>
</div>
""",
    },
    "video-to-transcript": {
        "title": "Video to Transcript \u2014 Turn Any Video Into Usable Text With TranscriptX",
        "description": "Convert any video into clean, accurate transcript text with TranscriptX. Works with YouTube, TikTok, Instagram, and 1000+ platforms.",
        "keywords": "video to transcript, transcript from video, transcript video, video transcript",
        "h1": "Turn Any Video Into Clean, Publishable Transcript Text",
        "quick_answer": "TranscriptX converts video from any supported platform into accurate transcript text in minutes \u2014 ready for editing, publishing, and repurposing.",
        "faq": [
            {
                "q": "What platforms does TranscriptX support?",
                "a": "YouTube, TikTok, Instagram, X (Twitter), Facebook, and 1000+ other platforms with public video."
            },
            {
                "q": "How accurate is the video-to-transcript conversion?",
                "a": "TranscriptX uses our AI engine trained on hundreds of thousands of hours of real-world audio. Accuracy is high for clear speech and strong even with background noise."
            },
            {
                "q": "Can I transcribe videos in languages other than English?",
                "a": "Yes. TranscriptX supports multilingual transcription across dozens of languages."
            },
            {
                "q": "How long does transcription take?",
                "a": "Most videos are transcribed within minutes, depending on length and current demand."
            },
            {
                "q": "Do I need to download the video first?",
                "a": "No. Paste the URL and TranscriptX handles audio extraction automatically."
            },
        ],
        "body_html": """
<p>Video is everywhere. Your team records product demos. Your founder does podcast interviews. Your marketing lead goes live on Instagram. Your sales team runs webinars. All of that content has value beyond the moment it was spoken \u2014 but only if you can get it into text.</p>

<p>TranscriptX turns video from any supported platform into clean transcript text in minutes. No file downloads, no audio conversion, no manual typing. Paste a URL and get text you can actually use.</p>

<h2>The problem with video-only content</h2>

<p>Video content has a discoverability problem. Search engines can crawl text, not speech. Social algorithms surface video briefly, then move on. Internal teams cannot search spoken words in a Zoom recording. The insight, the quote, the step-by-step explanation \u2014 all of it stays locked inside a media file that most people will never rewatch.</p>

<p>Transcription unlocks that content. A single 10-minute video becomes a searchable document, a source for articles, a reference for your team, and an accessibility asset for audiences who prefer or need text. But traditional transcription \u2014 whether manual or through clunky desktop software \u2014 takes too long for teams publishing on a regular schedule.</p>

<h2>How TranscriptX converts video to transcript</h2>

<p>TranscriptX works with a URL. That is the starting point and, from your perspective, nearly the entire workflow.</p>

<p>You paste a video URL from YouTube, TikTok, Instagram, X, Facebook, or any of 1000+ supported sources. TranscriptX extracts the audio track automatically behind the scenes. The audio is then processed through our speech recognition engine \u2014 AI trained on hundreds of thousands of hours of diverse, real-world audio spanning dozens of languages and conditions.</p>

<p>Within minutes, you receive a clean transcript. Not a raw character dump \u2014 readable text with coherent sentence structure that you can immediately start editing for your target format.</p>

<h2>What makes TranscriptX different</h2>

<p><strong>Platform breadth.</strong> Most transcription tools are YouTube-only or require you to upload files. TranscriptX supports 1000+ sources because it handles audio extraction from URLs directly. If there is a public video at a URL, TranscriptX can likely transcribe it.</p>

<p><strong>AI quality.</strong> Modern AI transcription engines are a meaningful leap over older systems. Unlike legacy tools that were trained on narrow, clean datasets, today's engines are trained on massive volumes of actual web audio \u2014 with all its imperfections. That is why TranscriptX handles background noise, accents, technical jargon, and multilingual content substantially better than older solutions.</p>

<p><strong>Operational resilience.</strong> Platforms change. Extraction paths break. Request patterns get throttled. TranscriptX handles this with automatic retries, intelligent proxy fallback for YouTube, and clear error messaging. You get a transcript or you get a real explanation \u2014 not a spinning loader that never resolves.</p>

<p><strong>Simplicity.</strong> No software to install. No audio files to manage. No API keys to configure. Paste a URL, click transcribe, get text. The complexity is handled for you.</p>

<h2>What teams build from transcripts</h2>

<p>The transcript is the starting material, not the final product. Here is what teams actually do with TranscriptX output:</p>

<p><strong>Content marketing teams</strong> turn one video into an SEO article, 3\u20135 social posts, and a newsletter section. One recording session feeds an entire week of content distribution.</p>

<p><strong>Product teams</strong> transcribe demo recordings and customer calls to build searchable knowledge bases, FAQ pages, and onboarding documentation.</p>

<p><strong>Agency teams</strong> batch-transcribe client content to produce deliverables faster. When your clients produce video weekly and expect written assets in return, TranscriptX compresses the turnaround from days to hours.</p>

<p><strong>Educators and researchers</strong> convert lectures, interviews, and conference talks into citable text documents. Transcripts become study materials, reference archives, and collaboration tools.</p>

<h2>Pricing built for real usage</h2>

<p>TranscriptX is not priced for enterprises with procurement departments. It is priced for creators and small teams who need reliable output at reasonable cost. Free gets you 3 transcripts/month. Starter is $2/month for 50. Pro is $4/month for unlimited. No per-minute billing, no hidden fees.</p>

<h2>FAQ</h2>
<h3>What platforms does TranscriptX support?</h3>
<p>YouTube, TikTok, Instagram, X (Twitter), Facebook, and 1000+ other platforms with public video.</p>
<h3>How accurate is the video-to-transcript conversion?</h3>
<p>TranscriptX uses our AI engine trained on hundreds of thousands of hours of real-world audio. Accuracy is high for clear speech and strong even with background noise.</p>
<h3>Can I transcribe videos in languages other than English?</h3>
<p>Yes. TranscriptX supports multilingual transcription across dozens of languages.</p>
<h3>How long does transcription take?</h3>
<p>Most videos are transcribed within minutes, depending on length and current demand.</p>
<h3>Do I need to download the video first?</h3>
<p>No. Paste the URL and TranscriptX handles audio extraction automatically.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Turn your next video into publishable text.</strong></p>
  <a href="/" style="color:#F0A860;font-weight:700;">Try TranscriptX free \u2192</a>
</div>
""",
    },
    "download-youtube-transcript": {
        "title": "Download YouTube Transcript \u2014 Get the Full Text Instantly",
        "description": "Download the full transcript from any YouTube video with TranscriptX. Clean AI-generated text even when native captions are missing or unreliable.",
        "keywords": "download youtube transcript, youtube transcript download, yt transcript, get transcript of youtube video",
        "h1": "Download YouTube Transcript \u2014 Full Text, Any Video, Instantly",
        "quick_answer": "TranscriptX lets you download a clean transcript from any YouTube video in minutes \u2014 even when native captions are unavailable or low-quality.",
        "faq": [
            {
                "q": "Can I download a transcript from any YouTube video?",
                "a": "Yes. TranscriptX extracts audio and generates its own transcript, so it works even when the video has no captions."
            },
            {
                "q": "Is the downloaded transcript better than YouTube's auto-captions?",
                "a": "In most cases, yes. TranscriptX uses our AI engine that handles noise, accents, and technical terms more accurately."
            },
            {
                "q": "What format is the transcript in?",
                "a": "TranscriptX returns clean, readable text that you can copy, edit, and paste into any editor or CMS."
            },
            {
                "q": "Does it work on mobile?",
                "a": "TranscriptX is a web app that works on any device with a browser."
            },
            {
                "q": "Is it free?",
                "a": "Free users get 3 transcripts/month. Paid plans start at $2/month for 50 transcripts."
            },
        ],
        "body_html": """
<p>You found a YouTube video with exactly the information you need. Maybe it is a 45-minute conference talk, a product breakdown, or an interview with someone in your industry. You want the text. You go to click \u201cShow Transcript\u201d \u2014 and it is not there. Or it is there, but the auto-generated captions are a mess of garbled sentences and missing punctuation.</p>

<p>This is the reality of downloading YouTube transcripts through native tools. It works sometimes. It fails often enough to be unreliable for anyone who depends on transcript output for real work.</p>

<p>TranscriptX solves this by not depending on YouTube\u2019s caption system at all. Paste the video URL, and TranscriptX extracts the audio directly and runs its own AI transcription. You get a clean, accurate transcript every time \u2014 regardless of whether the original video has captions enabled.</p>

<h2>Why native YouTube transcripts fall short</h2>

<p>YouTube\u2019s built-in transcript feature is tied to the caption track. If captions exist, you can view and copy the text. If they do not, there is nothing to download. Even when auto-captions are available, they come with well-documented limitations.</p>

<p>YouTube\u2019s own help documentation acknowledges that automatic captions may misrepresent content due to mispronunciations, accents, dialects, or background noise. For someone taking quick personal notes, that is acceptable. For someone creating published content, building documentation, or extracting precise quotes, it is not.</p>

<p>There is also the formatting problem. YouTube caption text is segmented for display timing, not for reading. When you copy it, you get choppy fragments that need significant restructuring before they resemble readable paragraphs. What feels like a simple \u201cdownload\u201d turns into a full editing project.</p>

<h2>How TranscriptX handles YouTube transcripts</h2>

<p>TranscriptX bypasses the caption dependency entirely. When you paste a YouTube URL, it extracts the actual audio track from the video. That audio is processed through our speech recognition engine \u2014 an AI model trained on hundreds of thousands of hours of multilingual, real-world audio data.</p>

<p>The result is a transcript generated from the spoken words themselves, not from a pre-existing caption file. This means you get output even when captions are disabled, missing, or auto-generated with poor quality.</p>

<p>The output is clean, paragraph-structured text. Not timestamped caption fragments. Not raw speech-to-text noise. Actual readable text that you can copy into a document and start editing immediately.</p>

<h2>What people actually use downloaded transcripts for</h2>

<p><strong>Content repurposing.</strong> A downloaded transcript is the fastest path from someone else\u2019s insight to your own published commentary. Transcribe a conference talk, extract the key arguments, add your perspective, and publish an article that would have taken hours to write from scratch.</p>

<p><strong>Research and citation.</strong> When you are writing about a topic and need to accurately quote or reference what someone said in a video, a transcript gives you searchable, citable text instead of scrubbing through a timeline.</p>

<p><strong>Meeting and lecture notes.</strong> Recorded Zoom calls shared on YouTube, university lectures, and webinar replays all become far more useful as text. Your team can search, highlight, and reference specific points instead of rewatching entire recordings.</p>

<p><strong>Accessibility and translation.</strong> Transcripts make video content available to people who are deaf or hard of hearing, and they provide a foundation for translation into other languages. If your audience is global, transcripts are not optional \u2014 they are infrastructure.</p>

<h2>Reliability when YouTube makes it hard</h2>

<p>Anyone who has worked with YouTube extraction at scale knows that the platform periodically changes how it serves content. Anti-bot checks, request throttling, and delivery pattern changes can break tools that worked yesterday. TranscriptX is built with this reality in mind.</p>

<p>The system includes automatic retries with backoff, rotating proxy fallback for YouTube-specific anti-bot detection, and clear error messaging when issues occur. If a transcript cannot be generated, TranscriptX tells you why and what to try next. You are never stuck wondering why the screen is blank.</p>

<h2>Simple pricing for regular use</h2>

<p>If you download transcripts occasionally, the free tier gives you 3 per month with no signup required. If transcription is part of your regular workflow, Starter at $2/month gives you 50, and Pro at $4/month gives you unlimited. No per-minute charges, no surprise bills.</p>

<h2>FAQ</h2>
<h3>Can I download a transcript from any YouTube video?</h3>
<p>Yes. TranscriptX extracts audio and generates its own transcript, so it works even when the video has no captions.</p>
<h3>Is the downloaded transcript better than YouTube\u2019s auto-captions?</h3>
<p>In most cases, yes. TranscriptX uses our AI engine that handles noise, accents, and technical terms more accurately.</p>
<h3>What format is the transcript in?</h3>
<p>TranscriptX returns clean, readable text that you can copy, edit, and paste into any editor or CMS.</p>
<h3>Does it work on mobile?</h3>
<p>TranscriptX is a web app that works on any device with a browser.</p>
<h3>Is it free?</h3>
<p>Free users get 3 transcripts/month. Paid plans start at $2/month for 50 transcripts.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Download your first YouTube transcript now.</strong></p>
  <a href="/" style="color:#F0A860;font-weight:700;">Try TranscriptX free \u2192</a>
</div>
""",
    },
    "audio-to-transcript": {
        "title": "Audio to Transcript \u2014 Convert Any Recording to Editable Text",
        "description": "TranscriptX converts audio from any video source into clean, structured transcript text. Ready in minutes.",
        "keywords": "audio to transcript, transcript audio, audio transcription, convert audio to text",
        "h1": "Audio to Transcript \u2014 From Raw Recording to Publishable Text",
        "quick_answer": "TranscriptX extracts audio from any video URL and delivers an accurate, editable transcript in minutes \u2014 no uploads, no installs, no waiting.",
        "faq": [
            {
                "q": "Does TranscriptX work with audio-only content like podcasts?",
                "a": "TranscriptX works with any URL that contains audio or video. If your podcast episode is hosted at a public URL, it can be transcribed."
            },
            {
                "q": "What happens with poor audio quality?",
                "a": "our AI engine is trained on noisy real-world audio and handles imperfect recordings better than older transcription systems. Very poor audio may still reduce accuracy."
            },
            {
                "q": "Can I transcribe audio in multiple languages?",
                "a": "Yes. TranscriptX supports dozens of languages and can handle mixed-language audio."
            },
            {
                "q": "How is this different from dictation software?",
                "a": "Dictation software converts live speech in real time. TranscriptX converts recorded audio into polished transcript text for editing and publishing."
            },
            {
                "q": "What can I do with the transcript?",
                "a": "Edit it into articles, guides, social posts, documentation, show notes, or any text format your workflow requires."
            },
        ],
        "body_html": """
<p>Audio content is one of the most underused assets in content production. Podcasts, interviews, webinars, voice memos, earnings calls, customer conversations \u2014 all of them contain spoken material that could become searchable, publishable, shareable text. But it stays locked in audio because the conversion step has traditionally been painful.</p>

<p>Manual transcription is slow. Desktop software is clunky. Most online tools require you to download audio files, convert formats, and upload them somewhere. By the time you have a transcript, the publishing window has passed or your team has moved on to the next thing.</p>

<p>TranscriptX removes that friction. It extracts audio from any supported video URL and converts it into clean, editable transcript text using our AI engine \u2014 all within minutes, entirely in your browser.</p>

<h2>Why audio transcription still matters</h2>

<p>In a world that increasingly produces content in audio and video formats, text remains the backbone of discoverability. Search engines index text. Knowledge bases store text. Teams collaborate in documents, not audio files. Social platforms may favor video, but the ideas inside that video reach further when they also exist as written words.</p>

<p>For creators, this means every podcast episode is also a potential article. Every webinar is a potential guide. Every interview is a potential quote bank for weeks of social content. But only if the audio becomes text quickly enough to act on it.</p>

<p>For teams, audio transcription turns ephemeral conversations into searchable records. Customer calls become training material. Strategy sessions become reference documents. The institutional knowledge that currently lives in recordings becomes accessible to everyone, not just the people who were in the room.</p>

<h2>How TranscriptX converts audio to transcript</h2>

<p>The process is built around one principle: you should not have to think about audio files. TranscriptX handles extraction and conversion behind the scenes.</p>

<p>You paste a URL \u2014 from YouTube, TikTok, Instagram, or any of 1000+ supported platforms. TranscriptX identifies and extracts the audio track. That audio is processed through our AI engine speech recognition, a model trained on hundreds of thousands of hours of real-world audio spanning dozens of languages and recording conditions.</p>

<p>You receive clean text output. Not timestamped fragments. Not raw speech-to-text noise. Structured, readable text that reflects what was actually said, with the coherence and sentence structure needed for editing.</p>

<h2>Why audio quality is not the dealbreaker it used to be</h2>

<p>Older transcription systems were trained on clean, studio-quality recordings. That made them brittle. Background noise, overlapping speakers, room echo, phone-quality microphones \u2014 any of these could degrade output to the point of uselessness.</p>

<p>Modern speech-recognition models are different because their training data is different. They were trained on massive volumes of actual web audio with all its imperfections. That broad training base gives them substantially better robustness to real recording conditions. Research indicates these models produce up to 50% fewer errors than systems trained on narrow benchmark datasets.</p>

<p>Does that mean perfect transcripts from terrible audio? No. Physics still applies \u2014 a recording with constant construction noise and three people talking at once will challenge any system. But for the vast majority of real content \u2014 podcast interviews, conference talks, product demos, customer calls \u2014 the output is immediately usable with minimal editing.</p>

<h2>From transcript to finished content</h2>

<p>The transcript is your raw material. What you build from it depends on your goal.</p>

<p><strong>Podcast show notes.</strong> Pull key topics, timestamps, and guest quotes from the transcript. Publish structured show notes that give listeners a reason to bookmark your episode page \u2014 and give search engines text to index.</p>

<p><strong>Long-form articles.</strong> A 30-minute conversation easily yields 4,000+ words of raw material. Extract the strongest arguments, add context and structure, and publish an article that would have taken a full day to write from scratch.</p>

<p><strong>Internal documentation.</strong> Customer call recordings become searchable support references. Onboarding sessions become training guides. Strategy conversations become decision logs. Transcripts turn audio archives into operational assets.</p>

<p><strong>Social content.</strong> Short, quotable moments from audio make excellent social posts. Transcripts let you find these moments by reading instead of re-listening, cutting production time dramatically.</p>

<h2>What TranscriptX costs</h2>

<p>TranscriptX is priced for real usage, not theoretical enterprise scale. Free users get 3 transcripts per month. Starter is $2/month for 50 transcripts. Pro is $4/month for unlimited. That is less than the cost of a single freelance transcription job.</p>

<h2>FAQ</h2>
<h3>Does TranscriptX work with audio-only content like podcasts?</h3>
<p>TranscriptX works with any URL that contains audio or video. If your podcast episode is hosted at a public URL, it can be transcribed.</p>
<h3>What happens with poor audio quality?</h3>
<p>our AI engine is trained on noisy real-world audio and handles imperfect recordings better than older transcription systems. Very poor audio may still reduce accuracy.</p>
<h3>Can I transcribe audio in multiple languages?</h3>
<p>Yes. TranscriptX supports dozens of languages and can handle mixed-language audio.</p>
<h3>How is this different from dictation software?</h3>
<p>Dictation software converts live speech in real time. TranscriptX converts recorded audio into polished transcript text for editing and publishing.</p>
<h3>What can I do with the transcript?</h3>
<p>Edit it into articles, guides, social posts, documentation, show notes, or any text format your workflow requires.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Turn your audio into content that works for you.</strong></p>
  <a href="/" style="color:#F0A860;font-weight:700;">Try TranscriptX free \u2192</a>
</div>
""",
    },
    "youtube-video-to-transcript": {
        "title": "YouTube Video to Transcript \u2014 From URL to Publishable Text",
        "description": "Convert any YouTube video to a clean, editable transcript with TranscriptX. Paste the URL, get accurate text in minutes, publish everywhere.",
        "keywords": "youtube video to transcript, youtube video transcript, transcript youtube video, youtube to transcript",
        "h1": "YouTube Video to Transcript \u2014 Paste a URL, Get Clean Text",
        "quick_answer": "TranscriptX converts any YouTube video into accurate, publication-ready transcript text in minutes. No captions required, no file downloads, no waiting.",
        "faq": [
            {
                "q": "How is this different from copying YouTube captions?",
                "a": "TranscriptX generates its own transcript from the audio, producing cleaner text than YouTube auto-captions with better punctuation and accuracy."
            },
            {
                "q": "What happens if YouTube blocks the video download?",
                "a": "TranscriptX includes retry logic and proxy fallback to handle YouTube anti-bot checks automatically."
            },
            {
                "q": "Can I turn the transcript into a blog post?",
                "a": "Yes. TranscriptX output is designed to be edited and restructured into articles, guides, and any text format."
            },
            {
                "q": "Does it work with YouTube Shorts?",
                "a": "Yes. Any YouTube URL with playable video content can be transcribed."
            },
            {
                "q": "How many YouTube videos can I transcribe?",
                "a": "Free: 3/month. Starter ($2/mo): 50. Pro ($4/mo): unlimited."
            },
            {
                "q": "Is the transcript available in other languages?",
                "a": "TranscriptX detects the spoken language automatically and supports dozens of languages."
            },
        ],
        "body_html": """
<p>YouTube is the largest library of spoken content on the internet. Tutorials, interviews, product reviews, conference keynotes, earnings calls, educational lectures \u2014 billions of hours of human knowledge and insight, all of it spoken, almost none of it available as clean text.</p>

<p>That gap represents a massive content opportunity. Every YouTube video your team watches, references, or creates is potential written content that could be driving search traffic, fueling social posts, and building your knowledge base. But the gap only closes if you can get from video to usable text quickly and reliably.</p>

<p>TranscriptX closes that gap. Paste a YouTube URL, get a clean transcript in minutes. No file downloads, no caption dependencies, no manual labor. Just text you can immediately edit and publish.</p>

<h2>The caption problem</h2>

<p>YouTube does offer a built-in transcript feature, and for casual use it works. But for anyone doing real content work, the limitations add up fast.</p>

<p>Auto-captions are generated by YouTube\u2019s own speech recognition and are explicitly described by YouTube as variable in quality. Names get mangled. Technical terms become unrecognizable. Punctuation is inconsistent or missing entirely. The text is segmented for caption display timing, not for reading \u2014 so even accurate captions produce choppy, fragmented output when copied.</p>

<p>And then there are the videos where captions simply do not exist. The creator disabled them, or the audio conditions prevented auto-generation, or the video is too new for captions to have processed. In those cases, YouTube\u2019s \u201cShow Transcript\u201d button does not appear at all. Your workflow hits a wall.</p>

<p>TranscriptX does not have this dependency. It extracts audio directly from the video and generates its own transcript using our AI engine. Captions being present or absent on YouTube is irrelevant to the output you receive.</p>

<h2>From YouTube URL to finished text</h2>

<p>Here is what the actual workflow looks like in practice.</p>

<p>You copy a YouTube video URL. You paste it into TranscriptX. Behind the scenes, TranscriptX downloads the audio track from the video. That audio is processed through speech recognition models trained on hundreds of thousands of hours of real-world, multilingual audio data. Within minutes, you have a clean transcript in your browser.</p>

<p>The transcript is structured for readability: coherent sentences, proper casing, natural paragraph flow. You can copy the full text with one click and paste it into your editor, CMS, Google Doc, or wherever your content workflow lives.</p>

<p>From there, the editorial work begins \u2014 but the hardest part is already done. Instead of staring at a blank page, you are reshaping existing substance. Instead of listening to a video at 1x speed with your fingers on a keyboard, you are scanning and editing text at the speed of reading.</p>

<h2>What one YouTube transcript becomes</h2>

<p>Think about the last time your team referenced a YouTube video in a meeting. Someone said \u201cthere is a great talk about this\u201d and shared a link. Two people watched part of it. Nobody had time to finish. The insight evaporated.</p>

<p>Now imagine that same video transcribed and published as an internal reference document within the hour. The key arguments are extracted. The relevant data points are highlighted. Anyone on the team can search the text, quote it, and build on it without watching 45 minutes of video. That is the operational value of video-to-transcript conversion.</p>

<p>For external content, the math is even more compelling. A single YouTube video can become a long-form article targeting a commercial keyword, a troubleshooting guide answering questions from the comments, a series of social posts pulling the best quotes, and an FAQ page addressing audience objections. One video, four assets, all indexable, all linkable, all working for you 24/7 while the original video\u2019s social visibility fades within days.</p>

<h2>Reliability matters more than features</h2>

<p>Anyone can build a transcription demo that works on a good day with a clean video. The real test is what happens on a bad day. YouTube changes delivery patterns. Anti-bot systems flag automated requests. Audio quality varies wildly across creators, devices, and environments.</p>

<p>TranscriptX is designed for this reality. The system includes automatic retries with backoff timing, proxy fallback for YouTube anti-bot detection, and transparent error messaging. When something goes wrong, you know what happened and what to do about it. When things work \u2014 which is most of the time \u2014 you barely notice the complexity underneath.</p>

<p>For teams that depend on transcription as part of a regular publishing workflow, this reliability is not a nice-to-have. It is the feature. A tool that works 70% of the time and fails silently the other 30% is worse than no tool at all, because you plan around it and then scramble when it breaks.</p>

<h2>Pricing for real people</h2>

<p>TranscriptX is priced so the decision is easy. Free users get 3 transcripts per month with no account required. Starter is $2/month for 50 transcripts with batch processing and export. Pro is $4/month for unlimited. That is less than a single cup of coffee for a tool that saves hours of manual work every month.</p>

<h2>FAQ</h2>
<h3>How is this different from copying YouTube captions?</h3>
<p>TranscriptX generates its own transcript from the audio, producing cleaner text than YouTube auto-captions with better punctuation and accuracy.</p>
<h3>What happens if YouTube blocks the video download?</h3>
<p>TranscriptX includes retry logic and proxy fallback to handle YouTube anti-bot checks automatically.</p>
<h3>Can I turn the transcript into a blog post?</h3>
<p>Yes. TranscriptX output is designed to be edited and restructured into articles, guides, and any text format.</p>
<h3>Does it work with YouTube Shorts?</h3>
<p>Yes. Any YouTube URL with playable video content can be transcribed.</p>
<h3>How many YouTube videos can I transcribe?</h3>
<p>Free: 3/month. Starter ($2/mo): 50. Pro ($4/mo): unlimited.</p>
<h3>Is the transcript available in other languages?</h3>
<p>TranscriptX detects the spoken language automatically and supports dozens of languages.</p>

<div style="margin-top:2rem;padding:1.5rem;background:#1a1a1a;border-radius:12px;text-align:center;">
  <p style="color:#C4C5C7;margin:0 0 0.5rem;"><strong>Turn any YouTube video into text you can use today.</strong></p>
  <a href="/" style="color:#F0A860;font-weight:700;">Try TranscriptX free \u2192</a>
</div>
""",
    },
}


register_page_routes(
    app,
    get_current_user=_get_current_user,
    get_banner=get_banner,
    checkout_starter=POLAR_CHECKOUT_STARTER,
    checkout_pro=POLAR_CHECKOUT_PRO,
    checkout_starter_annual=POLAR_CHECKOUT_STARTER_ANNUAL,
    checkout_pro_annual=POLAR_CHECKOUT_PRO_ANNUAL,
    customer_portal=POLAR_CUSTOMER_PORTAL,
    featurebase_app_id=FEATUREBASE_APP_ID,
    guides_content=GUIDES_CONTENT,
)


# ── Main Template ──────────────────────────────────────────

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX — Instant Transcripts from Any Video</title>
    <meta name="description" content="Transcribe any video instantly with AI. Supports YouTube, TikTok, Instagram, X, and 1000+ platforms. 99.2% accuracy, powered by TranscriptX.">
    <meta name="theme-color" content="#111111">
    <link rel="canonical" href="https://transcriptx.xyz/">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://transcriptx.xyz/">
    <meta property="og:title" content="TranscriptX — Instant Transcripts from Any Video">
    <meta property="og:description" content="Transcribe any video instantly with AI. Supports YouTube, TikTok, Instagram, X, and 1000+ platforms.">
    <meta property="og:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="TranscriptX — Instant Transcripts from Any Video">
    <meta name="twitter:description" content="Transcribe any video instantly with AI. 1000+ platforms supported.">
    <meta name="twitter:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script defer src="https://cloud.umami.is/script.js" data-website-id="ce056448-487b-4006-87df-54954128cff5"></script>
    <script>
        !(function(e,t){var a="featurebase-sdk";function n(){if(!t.getElementById(a)){var e=t.createElement("script");(e.id=a),(e.src="https://do.featurebase.app/js/sdk.js"),t.getElementsByTagName("script")[0].parentNode.insertBefore(e,t.getElementsByTagName("script")[0])}};"function"!=typeof e.Featurebase&&(e.Featurebase=function(){(e.Featurebase.q=e.Featurebase.q||[]).push(arguments)}),"complete"===t.readyState||"interactive"===t.readyState?n():t.addEventListener("DOMContentLoaded",n)})(window,document);
        if ("{{ config.featurebase_app_id }}") {
            Featurebase("boot", {
                appId: "{{ config.featurebase_app_id }}",
                theme: "dark",
                language: "en"
            });
        }
    </script>
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --electricgreen: #9BBA45;
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
        .transcript-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; gap:8px; flex-wrap:wrap; }
        .head-meta { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
        .head-actions { display:flex; align-items:center; gap:6px; }
        .copy-btn {
            background:none; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:3px 10px; font-size:0.55rem; cursor:pointer; font-family:var(--f-tech);
            text-transform:uppercase; transition:0.2s;
        }
        .copy-btn:hover { background:var(--ink); color:var(--orange); }
        .copy-btn.ok { background:var(--green); color:#fff; border-color:var(--green); }
        .transcript-text { font-size:0.82rem; line-height:1.7; opacity:0.8; }
        .transcript-text.hidden { display:none; }
        .view-btn {
            background:none; border:var(--bw) solid var(--ink); color:var(--ink);
            padding:3px 10px; font-size:0.55rem; cursor:pointer; font-family:var(--f-tech);
            text-transform:uppercase; transition:0.2s;
        }
        .view-btn:hover { background:var(--ink); color:var(--orange); }
        .timed-view { display:flex; flex-direction:column; gap:8px; }
        .timed-view.hidden { display:none; }
        .seg-row { display:grid; grid-template-columns:92px minmax(0,1fr); gap:10px; align-items:start; font-size:0.75rem; line-height:1.55; }
        .seg-time { font-weight:700; opacity:0.75; white-space:nowrap; }
        .seg-text { opacity:0.9; }
        .seg-empty { font-size:0.75rem; opacity:0.6; }

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
    {% if banner.enabled and banner.text %}
    <div id="siteBanner" style="background:var(--electricgreen);color:var(--ink);text-align:center;padding:0.6rem 2rem;font-size:0.7rem;font-family:var(--f-tech);position:relative;">
        {{ banner.text }}
        <button onclick="document.getElementById('siteBanner').remove()" style="position:absolute;right:1rem;top:50%;transform:translateY(-50%);background:none;border:none;font-size:1rem;cursor:pointer;opacity:0.6;">✕</button>
    </div>
    {% endif %}
    <div class="layout">
        <!-- Nav -->
        <nav>
            <div class="nav-logo">TRANSCRIPTX<em>®</em></div>
            <div class="nav-links">
                {% if user.logged_in %}
                <span class="nav-badge {{ user.plan }}">{{ user.plan_name }} — {{ user.credits_label }}</span>
                {% if user.plan != 'free' %}
                <a href="{{ config.customer_portal }}" data-umami-event="nav-billing">Billing</a>
                {% else %}
                <a href="/pricing" data-umami-event="nav-upgrade">Upgrade</a>
                {% endif %}
                <a href="/profile-links" data-umami-event="nav-links">Links</a>
                <a href="#" onclick="logout();return false" data-umami-event="nav-logout">Logout</a>
                {% else %}
                <a href="/profile-links" data-umami-event="nav-links">Links</a>
                <a href="#" onclick="showAuth('login');return false" data-umami-event="nav-login">Login</a>
                <a href="#" onclick="showAuth('signup');return false" data-umami-event="nav-signup">Sign Up</a>
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
                        <button id="goBtn" onclick="go()" data-umami-event="extract-transcript">EXTRACT ➔</button>
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
                <a href="/guides" style="display:block;text-align:center;padding:0.8rem 1rem;background:var(--grey);color:var(--ink);border-radius:12px;font-family:var(--f-tech);font-size:0.75rem;font-weight:700;text-decoration:none;text-transform:uppercase;letter-spacing:0.05em;">Guides &rarr;</a>
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
            <button class="export-btn" onclick="expCSV()" data-umami-event="export-csv">Export CSV</button>
            <button class="export-btn" onclick="expJSON()" data-umami-event="export-json">Export JSON</button>
            <button class="export-btn" onclick="clearAll()" data-umami-event="clear-results">Clear</button>
        </div>

        <!-- Results -->
        <div id="results"></div>

        <!-- Auth modal -->
        <div class="modal-overlay" id="authModal" onclick="if(event.target===this)hideAuth()">
            <div class="modal-box">
                <!-- Tab toggle -->
                <div id="authTabs" style="display:flex;gap:0;margin-bottom:1.2rem;">
                    <button class="auth-tab active" id="tabLogin" onclick="switchTab('login')" data-umami-event="tab-login">LOG IN</button>
                    <button class="auth-tab" id="tabSignup" onclick="switchTab('signup')" data-umami-event="tab-signup">SIGN UP</button>
                </div>

                <!-- Login form -->
                <div id="loginForm">
                    <input type="email" class="modal-input" id="loginEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="loginPassword" placeholder="Password" autocomplete="current-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doLogin()">
                    <div class="modal-err" id="loginErr"></div>
                    <button class="modal-btn" onclick="doLogin()" data-umami-event="login-submit">LOG IN ➔</button>
                </div>

                <!-- Signup form -->
                <div id="signupForm" style="display:none;">
                    <input type="email" class="modal-input" id="signupEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="signupPassword" placeholder="Password (6+ chars)" autocomplete="new-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doSignup()">
                    <div class="modal-err" id="signupErr"></div>
                    <button class="modal-btn" onclick="doSignup()" data-umami-event="signup-submit">SIGN UP ➔</button>
                </div>

                <!-- Verify form -->
                <div id="verifyForm" style="display:none;">
                    <div class="modal-title">Check Your Email</div>
                    <div class="modal-sub" id="verifySub">Enter the 6-digit code we sent</div>
                    <input type="text" class="modal-input" id="verifyCode" placeholder="000000" maxlength="6" style="text-align:center;font-size:1.5rem;letter-spacing:0.4em;" onkeydown="if(event.key==='Enter')doVerify()">
                    <div class="modal-err" id="verifyErr"></div>
                    <button class="modal-btn" onclick="doVerify()" data-umami-event="verify-submit">VERIFY ➔</button>
                    <div style="margin-top:0.8rem;text-align:center;">
                        <a href="#" onclick="resendCode();return false" style="font-size:0.7rem;color:var(--ink);opacity:0.5;" data-umami-event="resend-code">Resend code</a>
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

        function fmtSec(v) {
            const n = Number(v || 0);
            if (!Number.isFinite(n) || n < 0) return '0:00';
            const m = Math.floor(n / 60);
            const s = Math.floor(n % 60);
            return `${m}:${String(s).padStart(2, '0')}`;
        }

        function esc(v) {
            return String(v || '')
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll('"', '&quot;');
        }

        function segmentsHtml(segments) {
            if (!segments.length) return '<div class="seg-empty">No timestamp segments returned.</div>';
            return segments.map((seg) => `
                <div class="seg-row">
                    <span class="seg-time">${fmtSec(seg.start)}-${fmtSec(seg.end)}</span>
                    <span class="seg-text">${esc(seg.text || '')}</span>
                </div>
            `).join('');
        }

        function toggleTsView(baseId) {
            const plain = document.getElementById(baseId + '-plain');
            const timed = document.getElementById(baseId + '-timed');
            const btn = document.getElementById(baseId + '-toggle');
            if (!plain || !timed || !btn) return;
            const showTimed = timed.classList.contains('hidden');
            timed.classList.toggle('hidden', !showTimed);
            plain.classList.toggle('hidden', showTimed);
            btn.textContent = showTimed ? 'TEXT' : 'TIMED';
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
            const id = 'tx-'+Date.now()+'-'+Math.floor(Math.random()*100000);
            const segments = Array.isArray(d.segments) ? d.segments : [];
            const words = Array.isArray(d.words) ? d.words : [];
            const firstSeg = segments[0];
            const tsLabel = firstSeg
                ? `${fmtSec(firstSeg.start)}–${fmtSec(firstSeg.end)}`
                : 'none';
            const timed = segmentsHtml(segments);
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
                            <div class="head-meta">
                                <span class="label" style="margin:0">${d.language||'auto'}</span>
                                <span class="label" style="margin:0;opacity:0.7;">TS ${segments.length}/${words.length} · ${tsLabel}</span>
                            </div>
                            <div class="head-actions">
                                <button class="view-btn" id="${id}-toggle" onclick="toggleTsView('${id}')">TIMED</button>
                                <button class="copy-btn" onclick="clip(this,'${id}-plain')" data-umami-event="copy-transcript">COPY</button>
                            </div>
                        </div>
                        <div class="transcript-text" id="${id}-plain">${d.transcript||'No transcript'}</div>
                        <div class="timed-view hidden" id="${id}-timed">${timed}</div>
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


# ── Guides Templates ───────────────────────────────────────

GUIDES_INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranscriptX Guides</title>
    <meta name="description" content="Actionable guides for transcription workflows, repurposing video content, and SEO publishing systems.">
    <meta name="robots" content="index,follow">
    <link rel="canonical" href="https://transcriptx.xyz/guides">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://transcriptx.xyz/guides">
    <meta property="og:title" content="TranscriptX Guides">
    <meta property="og:description" content="Actionable guides for transcription workflows, repurposing video content, and SEO publishing systems.">
    <meta name="twitter:card" content="summary">
    <style>
        :root {
            color-scheme: light dark;
            --bg: #f4f4f5;
            --card: #ffffff;
            --ink: #141414;
            --text: #141414;
            --muted: #4f4f55;
            --link: #b84b3f;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #050505;
                --card: #c4c5c7;
                --ink: #0a0a0a;
                --text: #c4c5c7;
                --muted: #b3b3bb;
                --link: #b84b3f;
            }
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: "Space Mono", monospace; }
        main { max-width: 900px; margin: 0 auto; padding: 2rem 1rem 4rem; }
        h1 { margin-bottom: 0.5rem; }
        p.lead { margin-top: 0; color: var(--muted); }
        .list { display: grid; gap: 1rem; margin-top: 1.5rem; }
        .item { background: var(--card); color: var(--ink); padding: 1rem 1.2rem; border-radius: 16px; }
        .item a { color: var(--ink); text-decoration: none; font-weight: 700; }
        .item a:hover { color: var(--link); }
        .item p { color: #2b2b2b; }
        @media (prefers-color-scheme: dark) { .item p { color: #2b2b2b; } }
        .topnav { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:0.5rem; }
        .topnav a { color:var(--text); text-decoration:none; font-size:0.8rem; font-weight:700; }
        .topnav a:hover { color:var(--link); }
        .topnav .logo { font-size:1rem; letter-spacing:0.02em; }
        .topnav .links { display:flex; gap:1rem; align-items:center; }
        .cta-banner { margin-top:2rem; padding:1.2rem; background:var(--card); color:var(--ink); border-radius:14px; text-align:center; }
        .cta-banner a { color:var(--link); font-weight:700; text-decoration:none; }
    </style>
</head>
<body>
    <main>
        <nav class="topnav">
            <a href="/" class="logo">TranscriptX</a>
            <div class="links">
                <a href="/">Transcribe</a>
                <a href="/pricing">Pricing</a>
                <a href="/guides">Guides</a>
            </div>
        </nav>
        <h1>TranscriptX Guides</h1>
        <p class="lead">Practical guides for repurposing video, running transcription workflows, and shipping SEO content faster.</p>
        <div class="list">
            {% for item in guides %}
            <article class="item">
                <a href="/guides/{{ item.slug }}">{{ item.title }}</a>
                <p>{{ item.description }}</p>
            </article>
            {% endfor %}
        </div>
        <div class="cta-banner">
            <p style="margin:0 0 0.3rem;font-weight:700;">Ready to transcribe?</p>
            <a href="/">Start transcribing free &rarr;</a>
        </div>
    </main>
</body>
</html>
"""


GUIDE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ guide.title }} | TranscriptX</title>
    <meta name="description" content="{{ guide.description }}">
    <meta name="keywords" content="{{ guide.keywords }}">
    <meta name="robots" content="index,follow">
    <link rel="canonical" href="https://transcriptx.xyz/guides/{{ slug }}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://transcriptx.xyz/guides/{{ slug }}">
    <meta property="og:title" content="{{ guide.title }}">
    <meta property="og:description" content="{{ guide.description }}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{{ guide.title }}">
    <meta name="twitter:description" content="{{ guide.description }}">
    <script type="application/ld+json">{{ article_schema_json | safe }}</script>
    <script type="application/ld+json">{{ faq_schema_json | safe }}</script>
    <style>
        :root {
            color-scheme: light dark;
            --bg: #f4f4f5;
            --card: #ffffff;
            --ink: #141414;
            --text: #141414;
            --muted: #3f3f46;
            --accent: #b84b3f;
            --table-bg: #ffffff;
            --table-border: #d1d1d6;
            --table-head: #f0f0f2;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #050505;
                --card: #c4c5c7;
                --ink: #0a0a0a;
                --text: #c4c5c7;
                --muted: #b3b3bb;
                --accent: #b84b3f;
                --table-bg: #efefef;
                --table-border: #b1b1b1;
                --table-head: #dddddd;
            }
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: "Space Mono", monospace; line-height: 1.6; }
        main { max-width: 860px; margin: 0 auto; padding: 2rem 1rem 4rem; }
        .nav { margin-bottom: 1.25rem; }
        .nav a { color: var(--text); text-decoration: none; opacity: 0.9; }
        .panel { background: var(--card); color: var(--ink); border-radius: 18px; padding: 1.2rem 1.4rem; margin: 1rem 0 1.25rem; }
        h1, h2, h3 { line-height: 1.25; }
        h1 { margin-bottom: 0.7rem; }
        h2 { margin-top: 1.3rem; }
        p, li { color: var(--muted); }
        a { color: var(--accent); }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; background: var(--table-bg); }
        th, td { border: 1px solid var(--table-border); padding: 0.6rem; text-align: left; color: #111; }
        th { background: var(--table-head); }
        .topnav { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:0.5rem; }
        .topnav a { color:var(--text); text-decoration:none; font-size:0.8rem; font-weight:700; }
        .topnav a:hover { color:var(--accent); }
        .topnav .logo { font-size:1rem; letter-spacing:0.02em; }
        .topnav .links { display:flex; gap:1rem; align-items:center; }
        .sticky-cta { position:sticky; bottom:0; background:var(--bg); border-top:1px solid var(--muted); padding:0.8rem 1rem; text-align:center; margin:2rem -1rem 0; }
        .sticky-cta a { color:var(--accent); font-weight:700; text-decoration:none; font-size:0.85rem; }
    </style>
</head>
<body>
    <main>
        <nav class="topnav">
            <a href="/" class="logo">TranscriptX</a>
            <div class="links">
                <a href="/">Transcribe</a>
                <a href="/pricing">Pricing</a>
                <a href="/guides">Guides</a>
            </div>
        </nav>
        <h1>{{ guide.h1 }}</h1>
        <div class="panel"><strong>Quick answer:</strong> {{ guide.quick_answer }}</div>
        {{ guide.body_html | safe }}
        <div class="sticky-cta">
            <a href="/">Try TranscriptX free &rarr;</a>
        </div>
    </main>
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
    <meta name="description" content="Simple pricing for TranscriptX. Starter plan at $2/mo for 50 transcripts, or Pro at $4/mo for unlimited. All 1000+ platforms included.">
    <meta name="theme-color" content="#111111">
    <link rel="canonical" href="https://transcriptx.xyz/pricing">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://transcriptx.xyz/pricing">
    <meta property="og:title" content="TranscriptX — Pricing">
    <meta property="og:description" content="Starter $2/mo for 50 transcripts. Pro $4/mo for unlimited. All 1000+ platforms included.">
    <meta property="og:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="TranscriptX — Pricing">
    <meta name="twitter:description" content="Starter $2/mo for 50 transcripts. Pro $4/mo for unlimited.">
    <meta name="twitter:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script defer src="https://cloud.umami.is/script.js" data-website-id="ce056448-487b-4006-87df-54954128cff5"></script>
    <script>
        !(function(e,t){var a="featurebase-sdk";function n(){if(!t.getElementById(a)){var e=t.createElement("script");(e.id=a),(e.src="https://do.featurebase.app/js/sdk.js"),t.getElementsByTagName("script")[0].parentNode.insertBefore(e,t.getElementsByTagName("script")[0])}};"function"!=typeof e.Featurebase&&(e.Featurebase=function(){(e.Featurebase.q=e.Featurebase.q||[]).push(arguments)}),"complete"===t.readyState||"interactive"===t.readyState?n():t.addEventListener("DOMContentLoaded",n)})(window,document);
        if ("{{ config.featurebase_app_id }}") {
            Featurebase("boot", {
                appId: "{{ config.featurebase_app_id }}",
                theme: "dark",
                language: "en"
            });
        }
    </script>
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
                <a href="{{ config.checkout_starter }}" class="plan-btn dark" style="margin-top:auto;" data-umami-event="checkout-starter">GET STARTER ➔</a>
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
                <a href="{{ config.checkout_pro }}" class="plan-btn green" style="margin-top:auto;" data-umami-event="checkout-pro">GET PRO ➔</a>
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
    <meta name="description" content="Extract all video links from any TikTok, YouTube, Instagram, or X profile. Links stream in live — no waiting. Powered by TranscriptX.">
    <meta name="theme-color" content="#111111">
    <link rel="canonical" href="https://transcriptx.xyz/profile-links">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://transcriptx.xyz/profile-links">
    <meta property="og:title" content="TranscriptX — Profile Link Extractor">
    <meta property="og:description" content="Extract all video links from any TikTok, YouTube, Instagram, or X profile. Links stream in live.">
    <meta property="og:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="TranscriptX — Profile Link Extractor">
    <meta name="twitter:description" content="Extract all video links from any social media profile. Links stream in live.">
    <meta name="twitter:image" content="https://transcriptx.xyz/android-chrome-512x512.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Michroma&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script defer src="https://cloud.umami.is/script.js" data-website-id="ce056448-487b-4006-87df-54954128cff5"></script>
    <script>
        !(function(e,t){var a="featurebase-sdk";function n(){if(!t.getElementById(a)){var e=t.createElement("script");(e.id=a),(e.src="https://do.featurebase.app/js/sdk.js"),t.getElementsByTagName("script")[0].parentNode.insertBefore(e,t.getElementsByTagName("script")[0])}};"function"!=typeof e.Featurebase&&(e.Featurebase=function(){(e.Featurebase.q=e.Featurebase.q||[]).push(arguments)}),"complete"===t.readyState||"interactive"===t.readyState?n():t.addEventListener("DOMContentLoaded",n)})(window,document);
        if ("{{ config.featurebase_app_id }}") {
            Featurebase("boot", {
                appId: "{{ config.featurebase_app_id }}",
                theme: "dark",
                language: "en"
            });
        }
    </script>
    <style>
        :root {
            --bg: #050505;
            --orange: #F0A860;
            --electricgreen: #9BBA45;
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
    {% if banner.enabled and banner.text %}
    <div id="siteBanner" style="background:var(--electricgreen);color:var(--ink);text-align:center;padding:0.6rem 2rem;font-size:0.7rem;font-family:var(--f-tech);position:relative;">
        {{ banner.text }}
        <button onclick="document.getElementById('siteBanner').remove()" style="position:absolute;right:1rem;top:50%;transform:translateY(-50%);background:none;border:none;font-size:1rem;cursor:pointer;opacity:0.6;">✕</button>
    </div>
    {% endif %}
    <div class="layout">
        <nav>
            <a class="nav-logo" href="/">TRANSCRIPTX<em>&reg;</em></a>
            <div class="nav-links">
                {% if user.logged_in %}
                <span class="nav-badge {{ user.plan }}">{{ user.plan_name }} — {{ user.credits_label }}</span>
                {% if user.plan != 'free' %}
                <a href="{{ config.customer_portal }}" data-umami-event="nav-billing">Billing</a>
                {% else %}
                <a href="/pricing" data-umami-event="nav-upgrade">Upgrade</a>
                {% endif %}
                <a href="/" data-umami-event="nav-transcribe">Transcribe</a>
                <a href="#" onclick="logout();return false" data-umami-event="nav-logout">Logout</a>
                {% else %}
                <a href="/" data-umami-event="nav-transcribe">Transcribe</a>
                <a href="#" onclick="showAuth('login');return false" data-umami-event="nav-login">Login</a>
                <a href="#" onclick="showAuth('signup');return false" data-umami-event="nav-signup">Sign Up</a>
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
                <button id="btn" onclick="go()" data-umami-event="extract-links">EXTRACT ➔</button>
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
            <button class="stop-btn" onclick="stop()" data-umami-event="stop-extraction">Stop</button>
        </div>

        <div class="err" id="err"></div>

        <div class="results" id="results">
            <div class="results-head">
                <h2><span id="count">0</span> Links Found</h2>
                <div class="btn-row">
                    <button class="btn-sm" onclick="copyAll()" data-umami-event="copy-all-links">Copy All</button>
                    <button class="btn-sm green" onclick="downloadTxt()" data-umami-event="download-txt">Download .txt</button>
                </div>
            </div>
            <div class="link-list" id="links"></div>
        </div>

        <!-- Auth modal -->
        <div class="modal-overlay" id="authModal" onclick="if(event.target===this)hideAuth()">
            <div class="modal-box">
                <div id="authTabs" style="display:flex;gap:0;margin-bottom:1.2rem;">
                    <button class="auth-tab active" id="tabLogin" onclick="switchTab('login')" data-umami-event="tab-login">LOG IN</button>
                    <button class="auth-tab" id="tabSignup" onclick="switchTab('signup')" data-umami-event="tab-signup">SIGN UP</button>
                </div>
                <div id="loginForm">
                    <input type="email" class="modal-input" id="loginEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="loginPassword" placeholder="Password" autocomplete="current-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doLogin()">
                    <div class="modal-err" id="loginErr"></div>
                    <button class="modal-btn" onclick="doLogin()" data-umami-event="login-submit">LOG IN ➔</button>
                </div>
                <div id="signupForm" style="display:none;">
                    <input type="email" class="modal-input" id="signupEmail" placeholder="Email" autocomplete="email">
                    <input type="password" class="modal-input" id="signupPassword" placeholder="Password (6+ chars)" autocomplete="new-password" style="margin-top:0.5rem;" onkeydown="if(event.key==='Enter')doSignup()">
                    <div class="modal-err" id="signupErr"></div>
                    <button class="modal-btn" onclick="doSignup()" data-umami-event="signup-submit">SIGN UP ➔</button>
                </div>
                <div id="verifyForm" style="display:none;">
                    <div class="modal-title">Check Your Email</div>
                    <div class="modal-sub" id="verifySub">Enter the 6-digit code we sent</div>
                    <input type="text" class="modal-input" id="verifyCode" placeholder="000000" maxlength="6" style="text-align:center;font-size:1.5rem;letter-spacing:0.4em;" onkeydown="if(event.key==='Enter')doVerify()">
                    <div class="modal-err" id="verifyErr"></div>
                    <button class="modal-btn" onclick="doVerify()" data-umami-event="verify-submit">VERIFY ➔</button>
                    <div style="margin-top:0.8rem;text-align:center;">
                        <a href="#" onclick="resendCode();return false" style="font-size:0.7rem;color:var(--ink);opacity:0.5;" data-umami-event="resend-code">Resend code</a>
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