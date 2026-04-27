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
from error_classifier import format_error_response

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
    generate_mcp_token, validate_mcp_token, revoke_mcp_token, list_user_mcp_tokens,
    link_polar_to_user,
    get_banner, set_config,
    claim_webhook_event,
    release_webhook_event,
    sync_polar_subscription_webhook,
    effective_entitlement,
)
from transcribe import process_url, download_video_mp4, clip_video_segment, _sanitize_filename
from routes_pages import register_page_routes
from seo_catalog import CURATED_PLATFORM_OVERRIDES, current_lastmod, get_platform_pages, get_static_seo_paths

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
    # Long-tail /platform/* pages are noindex'd in routes_pages._platform_robots,
    # so listing them here pollutes the sitemap quality signal (Google sees ~95%
    # of advertised URLs as noindex). Restoring the full list once those pages
    # are either deleted or promoted to real content (Track B / PLATFORM_GUIDES).
    # rows.extend((f"/platform/{slug}-transcript-generator", "0.7") for slug in sorted(get_platform_pages().keys()))
    rows.extend(
        (f"/platform/{slug}-transcript-generator", "0.7")
        for slug in sorted(get_platform_pages().keys())
        if slug in CURATED_PLATFORM_OVERRIDES
    )

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
                return jsonify({
                    "status": "error",
                    "error": "Too many requests",
                    "action": f"Wait {window_sec} seconds and try again",
                    "retry_after": window_sec,
                    "help_url": "/help"
                }), 429
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
        error_response = format_error_response(str(e), "language validation")
        return jsonify(error_response), 400

    if not url:
        log_transcript_attempt(user_id, email, url, "error_no_url", credits_used=0)
        return jsonify({"status": "error", "error": "No URL provided"}), 400

    if not url.startswith(("https://", "http://")):
        log_transcript_attempt(user_id, email, url, "error_invalid_url", credits_used=0)
        return jsonify({"status": "error", "error": "Invalid URL. Must start with https://"}), 400

    # Check + deduct credits
    if user["credits"] != -1 and user["credits"] <= 0:
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return jsonify({
            "status": "error",
            "error": "No credits remaining",
            "action": "Upgrade your plan to continue transcribing",
            "help_url": "/pricing",
            "current_credits": 0,
            "current_plan": user.get("plan_name", "Free"),
            "suggested_plan": "Starter" if user.get("plan_name") == "Free" else "Pro"
        }), 403
    if not use_credit_for_user(user["user_id"]):
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return jsonify({
            "status": "error",
            "error": "No credits remaining",
            "action": "Upgrade your plan to continue transcribing",
            "help_url": "/pricing",
            "current_credits": 0,
            "current_plan": user.get("plan_name", "Free"),
            "suggested_plan": "Starter" if user.get("plan_name") == "Free" else "Pro"
        }), 403

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


@app.route("/api/mcp/tokens", methods=["GET"])
def api_mcp_list_tokens():
    """List the current user's MCP tokens (active + revoked).

    Never returns the raw token or its hash — just the prefix the user
    can use to recognize which token is which in the UI.
    """
    user = _get_current_user()
    if not user.get("logged_in"):
        return jsonify({"status": "error", "error": "Login required"}), 401
    tokens = list_user_mcp_tokens(user["user_id"])
    return jsonify({"status": "ok", "tokens": tokens})


@app.route("/api/mcp/generate-token", methods=["POST"])
def api_mcp_generate_token():
    """Create a new MCP token for the current user. Returned ONCE.

    Caller must surface the raw token to the user immediately. We never
    show the raw token again — the UI shows only the prefix on subsequent
    visits.
    """
    user = _get_current_user()
    if not user.get("logged_in"):
        return jsonify({"status": "error", "error": "Login required"}), 401
    result = generate_mcp_token(user["user_id"])
    full_url = f"https://mcp.transcriptx.xyz/?token={result['token']}"
    return jsonify({
        "status": "ok",
        "token": result["token"],
        "token_id": result["token_id"],
        "prefix": result["prefix"],
        "url": full_url,
    })


@app.route("/api/mcp/revoke-token", methods=["POST"])
def api_mcp_revoke_token():
    """Revoke an MCP token by id. Scoped to the current user."""
    user = _get_current_user()
    if not user.get("logged_in"):
        return jsonify({"status": "error", "error": "Login required"}), 401
    data = request.get_json(silent=True) or {}
    token_id = data.get("token_id")
    if not token_id:
        return jsonify({"status": "error", "error": "token_id required"}), 400
    ok = revoke_mcp_token(token_id, user["user_id"])
    if not ok:
        return jsonify({"status": "error", "error": "Token not found or already revoked"}), 404
    return jsonify({"status": "ok"})


@app.route("/account/mcp")
def account_mcp_page():
    """Settings page for managing MCP tokens."""
    user = _get_current_user()
    if not user.get("logged_in"):
        return redirect("/?login=1")
    tokens = list_user_mcp_tokens(user["user_id"])
    return render_template("account_mcp.html", user=user, tokens=tokens)


@app.route("/mcp/setup")
def mcp_setup_page():
    """Public setup guide — no auth required. Per-client config snippets."""
    return render_template("mcp_setup.html")


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
    "transcribe-google-drive-video": {
        "title": "How to Transcribe a Google Drive Video (Without Downloading It)",
        "description": "Got a video sitting in Google Drive — a Zoom recording, a meeting export, a screen grab? Get a clean transcript in about 30 seconds without downloading anything.",
        "keywords": "transcribe google drive video, google drive transcript, zoom recording in drive transcript",
        "h1": "How to Transcribe a Google Drive Video (Without Downloading It)",
        "quick_answer": "Open the video in Drive, click Share, switch access to “Anyone with the link”, copy the link, paste it into TranscriptX. Done in about 30 seconds. No download, no plugin, no Drive permissions for us.",
        "faq": [
            {
                "q": "Do I have to make the video public?",
                "a": "No. “Anyone with the link” means only people who have the link can open it — and nobody at TranscriptX keeps the link after the transcript is generated. If you’re nervous, flip it back to Restricted once your transcript is done."
            },
            {
                "q": "Will this work on a Shared Drive?",
                "a": "Usually, yes — as long as the Shared Drive allows external link sharing. Some company Shared Drives force domain-only access; in that case the link won’t open from our servers. You’ll need to download the file and reupload it to your personal Drive."
            },
            {
                "q": "Does this work for Zoom cloud recordings that auto-save to Drive?",
                "a": "Yes. That’s actually the most common use of this guide — Zoom drops the .mp4 into Drive, you share the link, and you get a transcript without paying for Zoom AI Companion."
            },
            {
                "q": "How large a file can I transcribe?",
                "a": "TranscriptX handles anything Drive can store. Very long recordings (multi-hour) will take longer to transcribe, but there’s no hard file-size cap from our side on link-based transcription."
            }
        ],
        "body_html": """
<p>If your video is already in Google Drive, you don’t need to download it, convert it, or install anything. Just share the link and paste it.</p>
<h2>The 30-second answer</h2>
<p>Open the video in Drive. Click <strong>Share</strong>. Change access to <strong>Anyone with the link</strong>. Copy the link. Paste it into <a href=\"/\">TranscriptX</a>. That’s it.</p>
<h2>Step-by-step</h2>
<h3>1) Open the video in Drive</h3>
<p>Go to <a href=\"https://drive.google.com\" rel=\"nofollow\">drive.google.com</a> and click the video. Doesn’t matter if it’s in My Drive, a Shared Drive, or a folder someone shared with you — as long as you can play it, you can transcribe it.</p>
<p><em>[Screenshot: Drive file preview with the Share button visible top-right]</em></p>
<h3>2) Click Share and set “Anyone with the link”</h3>
<p>This is the one step people get stuck on. Click <strong>Share</strong> (top right). Under “General access”, change <strong>Restricted</strong> to <strong>Anyone with the link</strong>. You don’t need to add any email addresses. Viewer access is fine — we only need to read the file.</p>
<p><em>[Screenshot: Share dialog with General access dropdown open, “Anyone with the link” highlighted]</em></p>
<h3>3) Copy the link and paste it into TranscriptX</h3>
<p>Click <strong>Copy link</strong>, then paste it on <a href=\"/\">transcriptx.xyz</a>. Hit Transcribe. You’ll have a full transcript in under a minute for most videos.</p>
<p><em>[Screenshot: TranscriptX homepage input with a Drive link pasted and the Transcribe button highlighted]</em></p>
<p>Once you’ve got your transcript, you can flip the Drive link back to Restricted if you want. We don’t keep the link.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>“You need access” or “Not allowed to access this video.”</strong> Your share setting is still Restricted. Go back to Share and set it to Anyone with the link.</li>
  <li><strong>Shared Drive won’t open externally.</strong> Some company Shared Drives force domain-only sharing and block external link access. We can’t get past that. Download the file to your laptop, reupload it to your personal Drive, and share from there.</li>
  <li><strong>The video is actually a Google Doc / Slides / Form.</strong> Drive shows videos, but “video” has to mean a real video file (.mp4, .mov, .webm, .m4a for audio). Recorded Meet sessions and exported Zoom recordings are fine. Presentations aren’t.</li>
  <li><strong>Video has a Google-level DRM flag.</strong> Rare, but some company-uploaded videos are flagged and can’t be streamed from a share link. If a colleague uploaded it with restrictions, ask them to export and send the raw file instead.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a> — the most common Drive use case.</li>
  <li><a href=\"/guides/transcribe-microsoft-teams-recording\">How to transcribe a Microsoft Teams meeting</a> — same pattern, different host.</li>
  <li><a href=\"/guides/transcribe-loom-video\">How to transcribe a Loom video</a> — for the share-link flow with Loom.</li>
</ul>
<h2>Try it</h2>
<p>You get 3 free transcripts a month on TranscriptX. No signup needed for the first one — <a href=\"/\">paste your Drive link and go</a>. Pricing is on <a href=\"/pricing\">the pricing page</a> if you want more.</p>
""",
    },
    "transcribe-zoom-recording": {
        "title": "How to Transcribe a Zoom Recording (Without Paying for Zoom AI Companion)",
        "description": "Got a Zoom recording in the cloud or on your laptop? Get a clean transcript in under a minute — no Zoom AI Companion subscription needed.",
        "keywords": "transcribe zoom recording, zoom transcript free, zoom recording to text, zoom cloud recording transcript",
        "h1": "How to Transcribe a Zoom Recording (Without Paying for Zoom AI Companion)",
        "quick_answer": "If your Zoom recording is in the cloud, share the link and paste it on TranscriptX. If it’s on your laptop, drop it into Google Drive, share the Drive link, and paste that. Either way, no Zoom AI Companion needed.",
        "faq": [
            {
                "q": "Can TranscriptX open a Zoom Cloud link directly?",
                "a": "Yes, if the recording has a shareable link with no passcode (or the passcode removed). Most paid Zoom tiers give you this. Copy from zoom.us → Recordings → Share."
            },
            {
                "q": "What about a local recording on my laptop?",
                "a": "The cleanest path today is to drop the .mp4 into Google Drive, share the link publicly, and paste that link here."
            },
            {
                "q": "Doesn’t Zoom AI Companion already do this?",
                "a": "If you’re on a paid Zoom tier with AI Companion enabled, yes — but it’s priced per seat per month. TranscriptX is a flat $3.99/mo no matter how many recordings you run."
            },
            {
                "q": "Will it label speaker names?",
                "a": "Not by default — you get a clean transcript without diarization. For multi-person meetings, see the speaker-labeling guide."
            }
        ],
        "body_html": """
<p>Zoom has its own transcription now, but it’s tied to a paid AI Companion seat. If you already have the recording, you don’t need it.</p>
<h2>The 30-second answer</h2>
<p>Zoom recording in the cloud? Grab the share link and paste it. Recording on your laptop? Upload to Google Drive, share the link, paste that.</p>
<h2>Step-by-step — Zoom Cloud recording</h2>
<h3>1) Go to zoom.us → Recordings</h3>
<p>Sign in, click <strong>Recordings</strong> in the left nav, and find the meeting you want.</p>
<p><em>[Screenshot: Zoom Recordings page with one meeting highlighted]</em></p>
<h3>2) Share it publicly (no passcode)</h3>
<p>Click <strong>Share</strong>. Turn on <strong>Share this recording publicly</strong>. Turn off <strong>Passcode</strong> — our servers can’t type passcodes for you. Copy the link.</p>
<p><em>[Screenshot: Zoom Share dialog with public sharing on and passcode off]</em></p>
<h3>3) Paste into TranscriptX</h3>
<p>Drop the link on <a href=\"/\">transcriptx.xyz</a>, hit Transcribe. Done.</p>
<h2>Step-by-step — local recording (.mp4 on your laptop)</h2>
<p>Zoom saves local recordings to <code>~/Documents/Zoom/</code>. The cleanest path is to <a href=\"/guides/transcribe-google-drive-video\">drop it into Google Drive and share from there</a>.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Passcode on the cloud recording.</strong> We can’t type passcodes into Zoom. Remove the passcode, or host the file elsewhere.</li>
  <li><strong>“Only authenticated users can view.”</strong> Same problem — forces a Zoom login. Turn it off.</li>
  <li><strong>Expired recording.</strong> Free Zoom plans delete cloud recordings after a short retention window. If the link 404s, it’s gone.</li>
  <li><strong>Separate audio tracks.</strong> If you recorded with speaker-separated tracks, Zoom still exports one merged video by default. That’s what we transcribe.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-google-drive-video\">How to transcribe a Google Drive video</a> — for your local .mp4.</li>
  <li><a href=\"/guides/transcribe-microsoft-teams-recording\">How to transcribe a Microsoft Teams meeting</a> — same flow, different host.</li>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label who said what</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month, no signup for the first one. <a href=\"/\">Paste a Zoom or Drive link</a> and go. <a href=\"/pricing\">Pricing</a> if you need more.</p>
""",
    },
    "transcribe-tiktok-video": {
        "title": "How to Get the Transcript of a TikTok Video",
        "description": "Copy the share link from any public TikTok, paste it into TranscriptX, and you’ll have a clean transcript in about 20 seconds. Captions are not the same as a transcript.",
        "keywords": "tiktok transcript, transcribe tiktok video, tiktok to text, tiktok captions export",
        "h1": "How to Get the Transcript of a TikTok Video",
        "quick_answer": "Tap Share on the TikTok → Copy link → paste on TranscriptX. Works on any public video. Private accounts, draft videos, and some region-locked videos won’t open from our servers.",
        "faq": [
            {
                "q": "Isn’t this just the TikTok captions?",
                "a": "No. TikTok auto-captions are often incomplete or mistimed. We run Whisper on the actual audio, which gives you the full spoken content — including parts TikTok skipped."
            },
            {
                "q": "Does it work on private videos?",
                "a": "No. TikTok locks private videos behind login, and our servers don’t have an account. If it’s your own, flip it to public briefly."
            },
            {
                "q": "What if the video is music with no speech?",
                "a": "You’ll get an empty or near-empty transcript. Nothing to transcribe, and we don’t identify songs."
            },
            {
                "q": "Will it work on TikTok Shop videos?",
                "a": "Usually yes — as long as the video is still live. Shop videos get pulled when products go out of stock."
            }
        ],
        "body_html": """
<p>TikTok has auto-captions, but they’re not downloadable and they skip words. If you want the real transcript — for show notes, accessibility, or research — just paste the link.</p>
<h2>The 20-second answer</h2>
<p>Tap <strong>Share</strong> on the TikTok, tap <strong>Copy link</strong>, paste it on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Open the TikTok and tap Share</h3>
<p>On the app or tiktok.com, tap the <strong>Share</strong> arrow (right side on mobile, below the video on desktop).</p>
<p><em>[Screenshot: TikTok video with the Share panel open]</em></p>
<h3>2) Tap Copy link</h3>
<p>The link looks like <code>tiktok.com/@user/video/1234567890</code>. The short <code>vm.tiktok.com</code> format also works.</p>
<h3>3) Paste into TranscriptX</h3>
<p>Open <a href=\"/\">transcriptx.xyz</a>, paste, hit Transcribe. 20-30 seconds later you have the text.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Private or Friends-only videos.</strong> TikTok requires a login we don’t have. If it’s yours, flip it to public briefly.</li>
  <li><strong>“Video unavailable in your region.”</strong> Our servers are in the US. Some videos are blocked outside the creator’s country.</li>
  <li><strong>Music-only videos.</strong> No speech = no transcript. Expected.</li>
  <li><strong>Live replays.</strong> These often aren’t shareable after the stream ends. If the replay is gone, it’s gone.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-instagram-reel-or-story\">How to transcribe an Instagram Reel</a> — same idea, different platform.</li>
  <li><a href=\"/guides/transcribe-youtube-short\">How to transcribe a YouTube Short</a>.</li>
  <li><a href=\"/guides/transcribe-facebook-video\">How to transcribe a Facebook video</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free TikToks a month, no signup for the first one. <a href=\"/\">Paste a link and go</a>.</p>
""",
    },
    "transcribe-private-youtube-video": {
        "title": "How to Transcribe a Private or Unlisted YouTube Video",
        "description": "Unlisted YouTube videos work like normal — paste the link, get a transcript. Private videos need a login we don’t have. Here’s what works and what doesn’t.",
        "keywords": "transcribe unlisted youtube video, private youtube transcript, unlisted youtube to text",
        "h1": "How to Transcribe a Private or Unlisted YouTube Video",
        "quick_answer": "Unlisted: copy the URL and paste it on TranscriptX — it works the same as a public video. Private: we can’t access it (YouTube requires login). Switch it to Unlisted, transcribe, switch back.",
        "faq": [
            {
                "q": "What’s the difference between Unlisted and Private?",
                "a": "Unlisted = anyone with the link can watch, but it won’t show up in search or on your channel. Private = only specific Google accounts you invited can see it. Unlisted is the sweet spot for transcription."
            },
            {
                "q": "Can I flip to Unlisted, transcribe, then flip back to Private?",
                "a": "Yes — that’s the standard workaround. Visibility changes instantly on YouTube; the link we used stops working the moment you switch back to Private."
            },
            {
                "q": "Do age-restricted videos work?",
                "a": "Usually no. YouTube requires a signed-in adult account, and we don’t have one."
            },
            {
                "q": "What about Members-only content?",
                "a": "Same problem — paid auth wall. Not supported."
            }
        ],
        "body_html": """
<p>YouTube has three visibility settings. Two work with us. One doesn’t.</p>
<h2>The 60-second answer</h2>
<p><strong>Unlisted:</strong> paste the URL on <a href=\"/\">TranscriptX</a>. <strong>Private:</strong> flip to Unlisted for a minute, transcribe, flip back.</p>
<h2>Which YouTube settings work</h2>
<ul>
  <li><strong>Public</strong> — works.</li>
  <li><strong>Unlisted</strong> — works. Anyone with the link can watch, including us.</li>
  <li><strong>Private</strong> — doesn’t work. Requires a Google login.</li>
  <li><strong>Members-only</strong> — doesn’t work. Paid auth wall.</li>
  <li><strong>Age-restricted</strong> — usually doesn’t work. Signed-in adult account required.</li>
</ul>
<h2>Step-by-step — Unlisted</h2>
<p>On the video page, click <strong>Share</strong> and copy the URL. Paste it on <a href=\"/\">transcriptx.xyz</a>. No prompt, no sign-in.</p>
<h2>Step-by-step — Private video you own</h2>
<p>Open YouTube Studio. Find the video. Under <strong>Visibility</strong>, switch from Private to <strong>Unlisted</strong>. Save. Copy the link. Paste on TranscriptX. Once the transcript is done, flip visibility back to Private.</p>
<p><em>[Screenshot: YouTube Studio Visibility dropdown with Unlisted selected]</em></p>
<h2>Common things that break</h2>
<ul>
  <li><strong>“Video unavailable” on an Unlisted video.</strong> The owner may have deleted it or switched back to Private.</li>
  <li><strong>Age-restricted content.</strong> Login wall, even on Unlisted.</li>
  <li><strong>Region-locked Unlisted.</strong> Rare but possible if the owner set it.</li>
  <li><strong>Premiere hasn’t aired.</strong> Nothing to transcribe yet — come back after the premiere.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-youtube-short\">How to transcribe a YouTube Short</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a YouTube video into show notes</a>.</li>
  <li><a href=\"/guides/transcribe-foreign-language-video\">How to transcribe a video in a different language</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month — <a href=\"/\">paste an unlisted link</a> and we’ll run it right now.</p>
""",
    },
    "transcribe-instagram-reel-or-story": {
        "title": "How to Transcribe an Instagram Reel or Story",
        "description": "Reels work with a link paste. Stories are ephemeral and auth-gated, so you’ll need a screen recording. Here’s the honest version of both.",
        "keywords": "transcribe instagram reel, instagram story transcript, reel to text",
        "h1": "How to Transcribe an Instagram Reel or Story",
        "quick_answer": "Reel: tap the paper-plane icon → Copy link → paste on TranscriptX. Any public Reel. Stories are harder — they expire in 24 hours and require login. Screen-record it from your phone, upload to Drive, paste the Drive link.",
        "faq": [
            {
                "q": "Why are Stories so hard?",
                "a": "Two reasons: they’re behind the Instagram login wall, and they self-delete after 24 hours. Our servers don’t have an Instagram account, and by the time we tried, the Story would often be gone."
            },
            {
                "q": "Does the paste flow work for Close Friends Stories?",
                "a": "No — Close Friends Stories are locked to specific accounts. Screen-record from your own account."
            },
            {
                "q": "What about Instagram Live replays?",
                "a": "If the creator saved the Live to their profile, yes — copy the URL from the saved post. Unsaved Lives disappear."
            },
            {
                "q": "Will it work on a private account’s Reel?",
                "a": "No. Private accounts require follower approval, and our servers aren’t followers."
            }
        ],
        "body_html": """
<p>Reels and Stories are both on Instagram, but technically they’re very different. One is easy to transcribe. One is genuinely hard.</p>
<h2>The 30-second answer</h2>
<p><strong>Reel:</strong> paper-plane icon → Copy link → paste on <a href=\"/\">TranscriptX</a>. <strong>Story:</strong> screen-record it from your phone, upload the recording to Google Drive, paste the Drive link.</p>
<h2>Step-by-step — Instagram Reel</h2>
<h3>1) Open the Reel and tap Share</h3>
<p>On the app or instagram.com, tap the paper-plane icon below the Reel (mobile) or the share arrow (desktop).</p>
<h3>2) Tap Copy link</h3>
<p>The URL format is <code>instagram.com/reel/ABC123xyz/</code>.</p>
<h3>3) Paste into TranscriptX</h3>
<p>Open <a href=\"/\">transcriptx.xyz</a>, paste, hit Transcribe.</p>
<h2>Step-by-step — Instagram Story (the harder case)</h2>
<p>Stories don’t have shareable links outside Instagram. The reliable path:</p>
<ul>
  <li>iPhone: open Control Center → Screen Record. Save to Photos.</li>
  <li>Android: pull down Quick Settings → Screen Recorder. Save to Gallery.</li>
  <li>Upload the recording to <a href=\"/guides/transcribe-google-drive-video\">Google Drive</a>, share publicly, paste on TranscriptX.</li>
</ul>
<h2>Common things that break</h2>
<ul>
  <li><strong>Private account Reels.</strong> Can’t get past the follower gate.</li>
  <li><strong>Expired Stories.</strong> 24 hours and gone. Screen-record before you forget.</li>
  <li><strong>Music-only Reels.</strong> No speech = no transcript.</li>
  <li><strong>Collab Reels.</strong> Posted to two accounts at once. Either account’s link works, as long as it’s public.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-tiktok-video\">How to transcribe a TikTok</a>.</li>
  <li><a href=\"/guides/transcribe-youtube-short\">How to transcribe a YouTube Short</a>.</li>
  <li><a href=\"/guides/transcribe-iphone-video\">How to transcribe a video on your iPhone</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a Reel link</a> and we’ll have the text in 20 seconds.</p>
""",
    },
    "transcribe-loom-video": {
        "title": "How to Transcribe a Loom Video",
        "description": "Loom has captions but no clean export. Paste the share link into TranscriptX and you’ll have a full, copyable transcript in under a minute.",
        "keywords": "transcribe loom video, loom transcript, loom to text, export loom captions",
        "h1": "How to Transcribe a Loom Video",
        "quick_answer": "Click Share on the Loom → Copy link → paste on TranscriptX. Works on free and paid Loom, on public and workspace-visible videos — as long as access is set to Anyone with the link.",
        "faq": [
            {
                "q": "Loom already shows captions. Why use TranscriptX?",
                "a": "Loom captions don’t export cleanly — you’d have to copy them line-by-line. We give you the transcript as plain text, SRT, VTT, or whatever format you need."
            },
            {
                "q": "Does it work on free-tier Loom videos?",
                "a": "Yes. Free videos are fine while they’re live. Free tier cleans up older storage, so if a Loom is expired, it’s gone for us too."
            },
            {
                "q": "Password-protected Loom?",
                "a": "Our servers can’t type passwords. Remove the password temporarily, transcribe, and put it back."
            },
            {
                "q": "Workspace-only Loom videos?",
                "a": "Those require a member login. Switch the access to Anyone with the link for the duration of the transcription."
            }
        ],
        "body_html": """
<p>Loom is everywhere in remote work. The captions exist but exporting them is annoying. Skip that step.</p>
<h2>The 30-second answer</h2>
<p>Click <strong>Share</strong> on the Loom, <strong>Copy link</strong>, paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Open the Loom and click Share</h3>
<p>On loom.com or the desktop app, click <strong>Share</strong> (top right).</p>
<p><em>[Screenshot: Loom video page with the Share button highlighted]</em></p>
<h3>2) Make sure it’s Anyone with the link</h3>
<p>Under <strong>Who has access</strong>, set to <strong>Anyone with the link</strong>. Workspace-only won’t work — our servers aren’t in your workspace.</p>
<h3>3) Copy link, paste on TranscriptX</h3>
<p>URL format is <code>loom.com/share/HEXSTRING</code>. Drop it on <a href=\"/\">transcriptx.xyz</a>.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Workspace-only access.</strong> Switch to Anyone with the link, or you’ll get a 403.</li>
  <li><strong>Password-protected.</strong> Remove the password for the duration.</li>
  <li><strong>Deleted or expired Loom.</strong> Free tier cleans up after quota. If the link 404s, the video is gone.</li>
  <li><strong>Embed-only share.</strong> Loom has an embed-only option that doesn’t produce a direct URL. Use the regular share link instead.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a>.</li>
  <li><a href=\"/guides/transcribe-microsoft-teams-recording\">How to transcribe a Microsoft Teams meeting</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a recording into show notes</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free Looms a month, no signup needed. <a href=\"/\">Paste a Loom link</a> and go.</p>
""",
    },
    "transcribe-vimeo-video": {
        "title": "How to Transcribe a Vimeo Video (Public, Password-Protected, or Private)",
        "description": "Three Vimeo privacy modes, three paths. Vimeo’s own captions are paywalled on Plus+ — here’s how to skip that.",
        "keywords": "transcribe vimeo video, vimeo transcript, vimeo captions free, private vimeo transcript",
        "h1": "How to Transcribe a Vimeo Video (Public, Password-Protected, or Private)",
        "quick_answer": "Public or Unlisted Vimeo: paste the URL. Password-protected: remove the password for a minute, transcribe, then put it back. Domain-locked or Vimeo OTT: we can’t reach those.",
        "faq": [
            {
                "q": "Isn’t Vimeo’s own captioning good enough?",
                "a": "Only on Plus+ plans. On free Vimeo, captions aren’t available without paying. Whisper is comparable quality and costs a flat $3.99/mo."
            },
            {
                "q": "How do I handle a password-protected video?",
                "a": "Temporarily remove the password in Privacy settings, run the transcript, re-add the password."
            },
            {
                "q": "Vimeo OTT or Showcase with a paywall?",
                "a": "Can’t access those — they require an account and payment."
            },
            {
                "q": "What’s the URL format?",
                "a": "Public and Unlisted look the same: <code>vimeo.com/123456789</code>. Both work."
            }
        ],
        "body_html": """
<p>Vimeo has three privacy modes that matter. Two work cleanly.</p>
<h2>The 30-second answer</h2>
<p><strong>Public / Unlisted:</strong> paste the URL on <a href=\"/\">TranscriptX</a>. <strong>Password-protected:</strong> remove the password, transcribe, put it back. <strong>Domain-locked / OTT:</strong> not reachable.</p>
<h2>Which privacy modes work</h2>
<ul>
  <li><strong>Public</strong> — works.</li>
  <li><strong>Unlisted</strong> — works.</li>
  <li><strong>Password-protected</strong> — works only if you remove the password temporarily.</li>
  <li><strong>Private (only me)</strong> — doesn’t work.</li>
  <li><strong>Embed-on-specific-domains</strong> — doesn’t work.</li>
  <li><strong>Vimeo OTT (subscription)</strong> — doesn’t work.</li>
</ul>
<h2>Step-by-step — public or unlisted</h2>
<p>Copy the video URL from the browser. Paste on <a href=\"/\">transcriptx.xyz</a>. Hit Transcribe.</p>
<h2>Step-by-step — password-protected (if you own it)</h2>
<p>Vimeo → your video → Settings → Privacy. Switch <strong>Who can watch</strong> to <strong>Anyone</strong>. Save. Transcribe. Switch the setting back.</p>
<p><em>[Screenshot: Vimeo Privacy settings with “Who can watch” dropdown open]</em></p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Password wall.</strong> Remove it or we can’t open the page.</li>
  <li><strong>“Unavailable in your region.”</strong> Rare, but possible on OTT or licensed content.</li>
  <li><strong>Embed-only video.</strong> “Hide this video from vimeo.com” breaks the direct URL path.</li>
  <li><strong>Multi-hour uploads.</strong> They work, but transcription time scales with length.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-private-youtube-video\">How to transcribe a private or unlisted YouTube video</a>.</li>
  <li><a href=\"/guides/transcribe-loom-video\">How to transcribe a Loom video</a>.</li>
  <li><a href=\"/guides/transcribe-webinar-for-blog\">How to transcribe a webinar for blog repurposing</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month — <a href=\"/\">paste a Vimeo link</a> now.</p>
""",
    },
    "transcribe-microsoft-teams-recording": {
        "title": "How to Transcribe a Microsoft Teams Meeting Recording",
        "description": "Teams transcripts require admin enablement most users don’t have. Use the SharePoint or OneDrive share link instead — here’s the step-by-step.",
        "keywords": "transcribe microsoft teams meeting, teams recording transcript, teams to text, sharepoint video transcript",
        "h1": "How to Transcribe a Microsoft Teams Meeting Recording",
        "quick_answer": "Teams recordings live in OneDrive (1:1s and group calls) or SharePoint (channel meetings). Open the recording, click Share, switch to Anyone with the link, paste the link on TranscriptX.",
        "faq": [
            {
                "q": "Doesn’t Teams already transcribe my meetings?",
                "a": "Only if your admin enabled transcription at the tenant level — many don’t. If there’s no Transcript tab on your recording, transcription was off during the meeting."
            },
            {
                "q": "Where does Teams save recordings?",
                "a": "Channel meetings → the SharePoint folder for that channel. 1:1s and group calls → the organizer’s OneDrive, in a folder called Recordings."
            },
            {
                "q": "My tenant blocks external sharing.",
                "a": "Then our servers can’t open the link. Download the recording, upload it to a personal cloud (Drive, Dropbox), and share that."
            },
            {
                "q": "Teams recordings expire after 120 days?",
                "a": "By default, yes. Your admin can change the retention policy."
            }
        ],
        "body_html": """
<p>Teams has built-in transcription, but only if your admin turned it on — and most didn’t. If you’re stuck with a recording and no transcript, this is the path.</p>
<h2>The 60-second answer</h2>
<p>Find the recording in <strong>OneDrive</strong> (1:1 or group call) or <strong>SharePoint</strong> (channel meeting). Click <strong>Share</strong>, change to <strong>Anyone with the link</strong>, copy, paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Find the recording</h3>
<p>Channel meeting: open the channel → <strong>Files</strong> → <strong>Recordings</strong>. 1:1 / group: OneDrive → <strong>My files</strong> → <strong>Recordings</strong>.</p>
<p><em>[Screenshot: OneDrive Recordings folder listing meeting videos]</em></p>
<h3>2) Click Share</h3>
<p>Hover the file, click the three-dot menu, pick <strong>Share</strong>.</p>
<h3>3) Change access to Anyone with the link</h3>
<p>If your tenant allows it, switch from “People in your organization” to <strong>Anyone with the link</strong>. Copy the link.</p>
<p><em>[Screenshot: SharePoint Share dialog with Anyone with the link selected]</em></p>
<h3>4) Paste on TranscriptX</h3>
<p>Open <a href=\"/\">transcriptx.xyz</a>, paste, transcribe.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>“Your organization doesn’t allow external sharing.”</strong> IT locked it down. Download the .mp4 and upload to a personal cloud instead.</li>
  <li><strong>Domain-restricted link.</strong> Some tenants force “anyone with the link at company.com”. Same fix — personal cloud workaround.</li>
  <li><strong>Recording auto-deleted.</strong> Default retention is 120 days.</li>
  <li><strong>Transcript tab exists but is empty.</strong> Audio issues during the meeting. Run our transcript on the recording directly.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a>.</li>
  <li><a href=\"/guides/transcribe-google-drive-video\">How to transcribe a Google Drive video</a> — for the personal-cloud fallback.</li>
  <li><a href=\"/guides/transcribe-sales-call-for-research\">How to transcribe a sales call</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a SharePoint or OneDrive link</a> now.</p>
""",
    },
    "transcribe-facebook-video": {
        "title": "How to Transcribe a Facebook Video or Live Stream",
        "description": "Facebook has auto-captions but no clean export. Paste the post URL into TranscriptX — works on public videos, Watch, and saved Live broadcasts.",
        "keywords": "transcribe facebook video, facebook live transcript, fb video to text",
        "h1": "How to Transcribe a Facebook Video or Live Stream",
        "quick_answer": "Open the video or Live on Facebook, copy the post URL from the browser, paste it on TranscriptX. Works on public posts, Pages, Watch, and saved Lives. Private groups and Messenger don’t work.",
        "faq": [
            {
                "q": "Facebook has auto-captions. Why do I need this?",
                "a": "Facebook doesn’t let you export the captions cleanly. We give you plain text, SRT, or VTT."
            },
            {
                "q": "Does it work on Facebook Watch?",
                "a": "Yes, as long as the Watch video is publicly visible. Age-gated or region-locked videos fail."
            },
            {
                "q": "Facebook Reels?",
                "a": "Yes, public Reels work the same way — copy URL, paste."
            },
            {
                "q": "Messenger videos?",
                "a": "No. Messenger content is behind your personal login."
            }
        ],
        "body_html": """
<p>Facebook auto-captions but won’t let you export them. Annoying. Paste the URL instead.</p>
<h2>The 30-second answer</h2>
<p>Click the timestamp on the post to open it as a standalone page. Copy the URL. Paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Open the Facebook video or Live</h3>
<p>On facebook.com, open the post. Desktop is easier — mobile app URLs are harder to grab.</p>
<h3>2) Copy the post URL</h3>
<p>Click the timestamp under the post (e.g. “2h ago”) to open the standalone page, then copy from the browser bar. Or click <strong>Share</strong> → <strong>Copy link</strong>.</p>
<p><em>[Screenshot: Facebook post with timestamp link highlighted]</em></p>
<h3>3) Paste on TranscriptX</h3>
<p>Drop it on <a href=\"/\">transcriptx.xyz</a>, hit Transcribe.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Private group videos.</strong> Gated behind membership. We can’t join groups.</li>
  <li><strong>Friends-only posts.</strong> Require your personal login.</li>
  <li><strong>Expired Lives.</strong> If the creator didn’t save the Live, it’s gone.</li>
  <li><strong>Age-gated videos.</strong> Facebook requires login for 18+ content.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-instagram-reel-or-story\">How to transcribe an Instagram Reel</a>.</li>
  <li><a href=\"/guides/transcribe-tiktok-video\">How to transcribe a TikTok</a>.</li>
  <li><a href=\"/guides/transcribe-webinar-for-blog\">How to transcribe a webinar for blog repurposing</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month — <a href=\"/\">paste a Facebook video link</a> now.</p>
""",
    },
    "transcribe-twitch-vod-or-clip": {
        "title": "How to Transcribe a Twitch VOD or Clip",
        "description": "VOD for reuploads, clip for highlights, both for copyright disputes — paste the Twitch URL, get a transcript in under a minute.",
        "keywords": "transcribe twitch vod, twitch clip transcript, twitch to text, twitch stream transcript",
        "h1": "How to Transcribe a Twitch VOD or Clip",
        "quick_answer": "Copy the VOD URL (twitch.tv/videos/123456789) or the clip URL (clips.twitch.tv/SomeName), paste on TranscriptX.",
        "faq": [
            {
                "q": "Why would I transcribe a stream?",
                "a": "YouTube reuploads with captions, sponsor segment summaries, copyright dispute evidence, editing highlights into clips, and searchable archives."
            },
            {
                "q": "How long do VODs last?",
                "a": "Partners: 60 days. Affiliates: 14 days. Regular users: 7 days. After that, unless the creator exported to Highlights, it’s gone."
            },
            {
                "q": "Subscriber-only VODs?",
                "a": "Don’t work. Twitch requires an authenticated subscriber session."
            },
            {
                "q": "Does it handle 6-hour streams?",
                "a": "Yes. Longer streams take proportionally longer to process but Whisper handles them cleanly."
            }
        ],
        "body_html": """
<p>Twitch keeps VODs for a short window. If you need the transcript, do it now.</p>
<h2>The 30-second answer</h2>
<p>Copy the URL — VODs look like <code>twitch.tv/videos/...</code>, clips look like <code>clips.twitch.tv/...</code>. Paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Find the VOD or clip</h3>
<p>twitch.tv → the channel → <strong>Videos</strong> (or <strong>Clips</strong>). Open the one you want.</p>
<h3>2) Copy the URL from the browser</h3>
<p>Regular streams become VODs automatically. Highlights and clips have permanent URLs.</p>
<h3>3) Paste on TranscriptX</h3>
<p>Long streams take a few minutes. Go grab coffee.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>VOD expired.</strong> 7 days for regular users, 14 for Affiliates, 60 for Partners.</li>
  <li><strong>Subscriber-only stream.</strong> Paywall. We can’t subscribe for you.</li>
  <li><strong>Stream muted for DMCA.</strong> Muted sections produce no transcript (silence).</li>
  <li><strong>Game-audio-only chunks.</strong> If the streamer lets the game narrate, expect a thin transcript.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a stream into YouTube show notes</a>.</li>
  <li><a href=\"/guides/transcribe-private-youtube-video\">How to transcribe a private or unlisted YouTube video</a>.</li>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label multiple speakers</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a Twitch link</a> and we’ll run it.</p>
""",
    },
    "interview-transcript-to-quotes": {
        "title": "How to Turn a 2-Hour Interview Into Quotes You Can Actually Use",
        "description": "Recording interviews is the easy part. Finding the 3 quotes that matter is where most people stall — here’s the workflow that doesn’t take all day.",
        "keywords": "interview transcript, podcast interview quotes, find quotes in transcript, interview workflow",
        "h1": "How to Turn a 2-Hour Interview Into Quotes You Can Actually Use",
        "quick_answer": "Transcribe the interview with TranscriptX. Ctrl-F the themes you care about. Copy the sentences you want with timestamps. Drop them into your doc. Whole thing is usually under 20 minutes, even on a 2-hour recording.",
        "faq": [
            {
                "q": "What format should I export?",
                "a": "Plain text is easiest to search. If you need to cite timestamps, export SRT or VTT and keep a second copy open."
            },
            {
                "q": "How do I handle multiple speakers?",
                "a": "Run the transcript, then add speaker names during your first read. AI diarization is ~80% right — which means 20% wrong, which is worse than taking 10 minutes yourself."
            },
            {
                "q": "Should I edit the quotes for clarity?",
                "a": "Yes, lightly. Remove filler (“um”, “like”) but keep the speaker’s cadence. Never add words they didn’t say."
            },
            {
                "q": "How many quotes should I pull?",
                "a": "Aim for 5-10 usable quotes per hour. More than that and you’re re-reporting. Fewer and you missed the substance."
            }
        ],
        "body_html": """
<p>Interviews are the raw material. Finding the 3 quotes that actually matter is the job.</p>
<h2>The 60-second answer</h2>
<p>Transcribe with <a href=\"/\">TranscriptX</a>. Open the text. Ctrl-F the themes you care about. Grab sentences with timestamps. Paste into your doc.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe the recording</h3>
<p>Paste the recording link on <a href=\"/\">TranscriptX</a>. If the recording is local, <a href=\"/guides/transcribe-google-drive-video\">drop it into Google Drive first</a>.</p>
<h3>2) Open the transcript in plain text</h3>
<p>We export .txt, .srt, .vtt, .json. Plain text is easiest to grep.</p>
<h3>3) Search for your themes</h3>
<p>Before reading, list the 3-5 themes you expected to hear — pricing concerns, team size, a specific objection. Ctrl-F each one and skim the surrounding paragraphs.</p>
<h3>4) Copy the quotes with timestamps</h3>
<p>For each usable quote, copy the sentence + SRT timestamp. Paste as:</p>
<pre><code>“This is the quote.” — Name, 00:23:14</code></pre>
<h3>5) Do a second pass for surprises</h3>
<p>Skim the sections you didn’t search for. Interviews usually have one line the person didn’t know they were going to say — that’s the quote you want.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Reading the whole transcript linearly.</strong> Waste of time. Search, don’t read.</li>
  <li><strong>Trusting AI speaker labels.</strong> They’re 80% right. Correct as you go.</li>
  <li><strong>Over-editing the quote.</strong> Remove filler. Keep the voice. Don’t smooth it into corporate.</li>
  <li><strong>Losing the timestamp.</strong> Always include it. You’ll thank yourself when you need to verify.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-sales-call-for-research\">How to transcribe a sales call for product research</a>.</li>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label multiple speakers</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn an interview into show notes</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your interview link</a> and get to the quotes in under 20 minutes.</p>
""",
    },
    "transcribe-lecture-for-study-notes": {
        "title": "How to Transcribe a Lecture for Study Notes (and Turn It Into Flashcards)",
        "description": "Turn a 60-minute lecture into searchable notes and Anki-ready flashcards in under 30 minutes. Works on Panopto, Echo360, Zoom, and YouTube recordings.",
        "keywords": "transcribe lecture for study, lecture to notes, lecture transcript to flashcards, panopto transcript",
        "h1": "How to Transcribe a Lecture for Study Notes (and Turn It Into Flashcards)",
        "quick_answer": "Get the lecture’s shareable link (Panopto, Echo360, Zoom cloud, YouTube). Paste on TranscriptX. Skim the transcript for key terms, bold them, convert definitions to flashcards.",
        "faq": [
            {
                "q": "My school uses Panopto or Echo360. Will this work?",
                "a": "If your lecture has a shareable link (most do), yes. If it’s locked to your LMS login only, you’ll need to download first — ask the professor, or use screen recording."
            },
            {
                "q": "How long does a 60-minute lecture take to transcribe?",
                "a": "Usually 2-3 minutes of processing. Much faster than real-time."
            },
            {
                "q": "Can I jump back to a specific moment from the transcript?",
                "a": "Yes, if you use the SRT or VTT export — timestamps are included."
            },
            {
                "q": "Will it handle heavy technical vocabulary (biochem, law)?",
                "a": "Whisper is strong on domain terms. Expect 90%+ accuracy on most subjects. Spot-check proper nouns."
            }
        ],
        "body_html": """
<p>The painful way to study from a lecture is to watch it twice. The faster way is to read it once.</p>
<h2>The 30-second answer</h2>
<p>Get the lecture’s share link. Paste on <a href=\"/\">TranscriptX</a>. Skim. Bold key terms. Convert to flashcards.</p>
<h2>Step-by-step</h2>
<h3>1) Get the lecture link</h3>
<p>Panopto / Echo360: right-click the video → Copy link. Zoom: the cloud-recording share link. YouTube: just the video URL.</p>
<h3>2) Paste on TranscriptX</h3>
<p>Drop the link on <a href=\"/\">transcriptx.xyz</a>. A 1-hour lecture takes 2-3 minutes.</p>
<h3>3) Skim for key terms</h3>
<p>Read fast. Bold every term the professor repeated or defined. Those are your flashcards.</p>
<h3>4) Convert to flashcards</h3>
<p>For each bolded term:</p>
<pre><code>Front: What is [term]?
Back: [definition in one sentence, lifted from the transcript]</code></pre>
<p>Paste into Anki, Quizlet, or RemNote.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>LMS-only video.</strong> Requires your school login. Our servers can’t sign in. Look for a Panopto share, or ask the professor.</li>
  <li><strong>Chalkboard / visual-heavy lectures.</strong> You’ll miss what’s on the board. Supplement with a photo or the slides.</li>
  <li><strong>Thick accent or poor audio.</strong> Accuracy drops. Use the language-retry feature if auto-detect picks the wrong language.</li>
  <li><strong>Proper nouns (people, papers).</strong> Always spot-check against the syllabus.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a> — for Zoom lectures.</li>
  <li><a href=\"/guides/transcribe-private-youtube-video\">How to transcribe a private YouTube video</a> — for unlisted lecture uploads.</li>
  <li><a href=\"/guides/transcribe-foreign-language-video\">How to transcribe a lecture in another language</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your lecture link</a> and start studying from text.</p>
""",
    },
    "youtube-video-to-show-notes": {
        "title": "How to Turn a YouTube Video Into Clean Show Notes With Timestamps",
        "description": "Podcaster and YouTube creator workflow: transcribe the episode, pull chapter markers, write a bullet summary, publish with timestamps.",
        "keywords": "youtube show notes, podcast show notes with timestamps, transcript to show notes, chapter markers from transcript",
        "h1": "How to Turn a YouTube Video Into Clean Show Notes With Timestamps",
        "quick_answer": "Transcribe the video with TranscriptX. Read the transcript, mark topic changes. Each topic becomes a chapter with an [HH:MM:SS] timestamp. One bullet per chapter. Publish.",
        "faq": [
            {
                "q": "What format should I export?",
                "a": "SRT or VTT, because they include timestamps. Skim the SRT, copy bullets to plain text for publishing."
            },
            {
                "q": "How many chapter markers should I add?",
                "a": "YouTube renders chapters if you have at least 3, each 10+ seconds long. 5-10 chapters per 30-minute episode feels right."
            },
            {
                "q": "Do chapter timestamps have to start at 0:00?",
                "a": "Yes — YouTube requires the first timestamp to be 00:00 for chapters to render."
            },
            {
                "q": "Can I automate this?",
                "a": "Partially. An LLM can draft bullet summaries from the transcript. A human pass is still what makes show notes readable."
            }
        ],
        "body_html": """
<p>Show notes are what your listeners actually read. Do them well and every episode becomes a findable page.</p>
<h2>The 60-second answer</h2>
<p>Transcribe on <a href=\"/\">TranscriptX</a>. Read once. Mark topic changes. Write each as a chapter. Bullet-summarize. Publish.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe in SRT format</h3>
<p>Paste the YouTube URL on <a href=\"/\">transcriptx.xyz</a>. Export SRT — timestamps are what you need.</p>
<h3>2) Read through and mark topic changes</h3>
<p>Scan the SRT for natural transitions. Note the timestamp where each new topic starts.</p>
<h3>3) Write the YouTube chapter list</h3>
<p>Format is strict — each line starts with a timestamp, first one must be 00:00:</p>
<pre><code>00:00 Intro and guest bio
02:15 How they got started
08:40 The first big mistake
...</code></pre>
<p>Paste this block into your YouTube video description. Chapters render on the scrubber automatically.</p>
<h3>4) One bullet per chapter for the written notes</h3>
<p>A bullet per chapter gives readers a map without spoiling the episode.</p>
<h3>5) Add callouts</h3>
<p>Names, tools, books, links mentioned — pull them into a “Mentioned in this episode” section.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>First chapter doesn’t start at 00:00.</strong> YouTube won’t render chapters. Always start at 00:00.</li>
  <li><strong>Chapters shorter than 10 seconds.</strong> YouTube merges or ignores them.</li>
  <li><strong>Too many chapters.</strong> 20+ on a 30-minute video reads like spam.</li>
  <li><strong>Copy-pasting transcript without editing.</strong> Spoken language is messier than written. Do the light pass.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to turn an interview into quotes</a>.</li>
  <li><a href=\"/guides/transcribe-webinar-for-blog\">How to transcribe a webinar for blog repurposing</a>.</li>
  <li><a href=\"/guides/transcribe-private-youtube-video\">How to transcribe an unlisted YouTube video</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your video URL</a> and start writing show notes readers actually read.</p>
""",
    },
    "transcribe-foreign-language-video": {
        "title": "How to Transcribe a Video in a Different Language (and Translate It)",
        "description": "Whisper auto-detects 90+ languages. If it guesses wrong, you can retry with the right language free. Then translate the output in one step.",
        "keywords": "transcribe foreign language video, translate video transcript, whisper language detection, multilingual transcription",
        "h1": "How to Transcribe a Video in a Different Language (and Translate It)",
        "quick_answer": "Paste the link — Whisper auto-detects the language. If it comes back in the wrong language, use the “retry with different language” option (free) and pick the correct one. Then paste the result into Google Translate or DeepL.",
        "faq": [
            {
                "q": "Which languages does Whisper handle?",
                "a": "90+ languages — Spanish, French, German, Portuguese, Arabic, Mandarin, Japanese, Korean, Hindi, and many more. Accuracy is strongest on the top 20."
            },
            {
                "q": "What if auto-detect picks the wrong language?",
                "a": "Hit the language retry on the result screen. It’s free — we don’t charge a second credit for a language correction."
            },
            {
                "q": "Can TranscriptX translate directly?",
                "a": "Not yet — we return the transcript in the spoken language. Paste into Google Translate, DeepL, or ChatGPT for the translation step."
            },
            {
                "q": "What about videos with mixed languages?",
                "a": "Whisper handles one dominant language well. If a video switches mid-way, expect patchy results. Transcribe each section separately if you can."
            }
        ],
        "body_html": """
<p>Whisper speaks 90+ languages. The trick is getting it to pick the right one.</p>
<h2>The 60-second answer</h2>
<p>Paste the video URL on <a href=\"/\">TranscriptX</a>. If the output looks wrong (garbled, wrong script), click the language retry and pick the correct language. Free. Then translate.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe normally</h3>
<p>Paste the URL. Let auto-detect do its thing.</p>
<h3>2) Check the output</h3>
<p>Does it match what you heard? If the video was Portuguese and the output is Spanish, auto-detect guessed wrong — common on similar-sounding languages.</p>
<h3>3) Use the language retry</h3>
<p>On the result screen, look for the “retry with different language” option. Pick the correct language. We rerun at no extra cost.</p>
<h3>4) Translate if you need it</h3>
<p>Paste the transcript into <a href=\"https://translate.google.com\" rel=\"nofollow\">Google Translate</a>, <a href=\"https://www.deepl.com\" rel=\"nofollow\">DeepL</a>, or an LLM. DeepL is usually cleaner for European languages.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Auto-detect picks a similar language.</strong> Portuguese → Spanish, Norwegian → Danish, Urdu → Hindi. Use the retry.</li>
  <li><strong>Code-switching mid-video.</strong> Whisper struggles if the speaker swaps languages every minute.</li>
  <li><strong>Heavy dialect.</strong> Accuracy drops on strong regional dialects. Still usable, spot-check.</li>
  <li><strong>Idioms in translation.</strong> Any translator fumbles idioms. Cross-check phrases that feel literal.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label multiple speakers</a>.</li>
  <li><a href=\"/guides/transcribe-lecture-for-study-notes\">How to transcribe a lecture</a>.</li>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to turn an interview into quotes</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month, retry language free. <a href=\"/\">Paste a link in any language</a> and go.</p>
""",
    },
    "transcribe-multi-speaker-video": {
        "title": "How to Transcribe a Video With Multiple Speakers and Label Who Said What",
        "description": "AI speaker labeling (diarization) is ~80% accurate — good enough to start from, not good enough to publish. Here’s the 2-minute fix that gets you to 100%.",
        "keywords": "multi-speaker transcript, diarization, label speakers in transcript, who said what transcript",
        "h1": "How to Transcribe a Video With Multiple Speakers and Label Who Said What",
        "quick_answer": "Transcribe the video. Do a 2-minute first-read and drop speaker names inline. It’s faster and more accurate than fixing AI labels — we intentionally don’t auto-label because the errors are worse than the help.",
        "faq": [
            {
                "q": "Why not automate speaker labels?",
                "a": "AI diarization is about 80% accurate under good conditions. On real recordings — overlapping speech, background noise, similar voices — it’s worse. Fixing wrong labels takes longer than labeling from scratch."
            },
            {
                "q": "How do I label efficiently?",
                "a": "Skim the transcript. Every time a new person starts talking, add a name. Usually 2-3 minutes for a 1-hour meeting."
            },
            {
                "q": "Can I ask an LLM to add labels after the fact?",
                "a": "Yes, and it helps for long interviews. Feed the transcript + a short description of each speaker (“A is the host, B is the guest CEO”) and it does a reasonable first pass."
            },
            {
                "q": "Is there a format that makes this easier?",
                "a": "Plain text with a line break between voice changes. Then you just prepend the name."
            }
        ],
        "body_html": """
<p>Labeling speakers sounds automatable. It isn’t — not reliably. This is a short human task that beats a long AI cleanup.</p>
<h2>The 60-second answer</h2>
<p>Transcribe the video on <a href=\"/\">TranscriptX</a>. First read-through, drop the speaker name at every voice change. Done.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe</h3>
<p>Paste your meeting recording link on <a href=\"/\">transcriptx.xyz</a>.</p>
<h3>2) Open the transcript with voice breaks visible</h3>
<p>Our default export uses a blank line between voice changes.</p>
<h3>3) Read fast, label inline</h3>
<p>Prepend each block with the speaker’s name:</p>
<pre><code>Sarah: We need to talk about the pricing page.
Alex: Agreed. What’s the current conversion?
Sarah: About 2.1% — lower than I thought.</code></pre>
<h3>4) Optional — LLM-assisted pass</h3>
<p>For longer interviews, paste the unlabeled transcript + a one-line speaker description into Claude or ChatGPT. Ask for labeled output. Not perfect but gets you to 90% on a 1-hour recording in seconds.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Trusting AI labels.</strong> Never publish them without a human check.</li>
  <li><strong>Overlapping speech.</strong> Nothing handles it well. Pick the dominant speaker.</li>
  <li><strong>Similar voices.</strong> Same-gender / same-accent confuses both AI and humans. Keep a short voice sample in mind.</li>
  <li><strong>4+ people on voice-only recording.</strong> Hard. Record per-speaker audio channels next time.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to turn an interview into quotes</a>.</li>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a>.</li>
  <li><a href=\"/guides/transcribe-sales-call-for-research\">How to transcribe a sales call</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a multi-person recording</a>.</p>
""",
    },
    "transcribe-webinar-for-blog": {
        "title": "How to Transcribe a Webinar or Conference Talk for Blog Repurposing",
        "description": "Turn a 45-minute webinar into a blog post, a LinkedIn summary, and three clip captions in under 90 minutes. End-to-end workflow most marketing teams never wrote down.",
        "keywords": "webinar to blog post, conference talk transcript, repurpose webinar, transcript for linkedin",
        "h1": "How to Transcribe a Webinar or Conference Talk for Blog Repurposing",
        "quick_answer": "Transcribe the webinar. Extract the 3-5 strongest points as the blog structure. Write each section in the speaker’s words. Reuse one punchy quote for LinkedIn. Grab timestamps for three short clips.",
        "faq": [
            {
                "q": "How long should the blog post be?",
                "a": "800-1,500 words covers a webinar without being a slog."
            },
            {
                "q": "Should I credit the speaker as the author?",
                "a": "If they wrote the talk, yes — and ask permission before publishing. Usually the company owns the recording, the speaker owns the ideas. Make that clear."
            },
            {
                "q": "Can I run it through an LLM?",
                "a": "For a first-draft skeleton, sure. For the final voice, a human edit is what makes the post sound like the speaker, not like ChatGPT."
            },
            {
                "q": "How many clips should I pull?",
                "a": "Three is a good target. One for LinkedIn, one for Twitter/X, one for Instagram or YouTube Shorts."
            }
        ],
        "body_html": """
<p>A webinar is a 45-minute asset your team produces once. Getting five pieces of content out of it is the job.</p>
<h2>The 90-second answer</h2>
<p>Transcribe the recording. 3-5 strongest points → blog structure. Rewrite each section in the speaker’s language. One quote → LinkedIn. Three timestamps → clips.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe the webinar recording</h3>
<p>Paste the replay URL on <a href=\"/\">TranscriptX</a>. Export SRT — you’ll need the timestamps for the clip step.</p>
<h3>2) Scan for 3-5 strongest points</h3>
<p>First read: mark the 3-5 sentences that made you sit up. Those are your blog sections.</p>
<h3>3) Write each section in the speaker’s words</h3>
<p>The goal isn’t a pristine ghost-written post. It’s a reader feeling they heard the talk. Keep the speaker’s idioms. Remove only filler.</p>
<h3>4) One quote → LinkedIn</h3>
<p>Pick the single best line. Post it as a pull quote. Credit the speaker and the event.</p>
<h3>5) Three clips → social</h3>
<p>Using the SRT timestamps, note three 30-60 second segments. Export clips (Descript, iMovie, any editor) and caption with the transcript text.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Publishing a lightly-edited transcript as the blog post.</strong> Reads like a transcript. Do the editorial pass.</li>
  <li><strong>Skipping speaker review.</strong> Especially external speakers. Send a draft.</li>
  <li><strong>Generic headline.</strong> The headline should be the speaker’s most quotable line — not “Webinar recap.”</li>
  <li><strong>Clipping without context.</strong> A 30-second clip without a setup line is useless. Show the question, then the payoff.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to write show notes with timestamps</a>.</li>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to find quotes in a transcript</a>.</li>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom webinar recording</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your webinar replay link</a> and start repurposing.</p>
""",
    },
    "transcribe-sales-call-for-research": {
        "title": "How to Transcribe a Sales Call or Customer Interview for Product Research",
        "description": "Gong and Fathom are great and expensive. If you just need the transcript to pull themes, quotes, and evidence — the cheap version is this.",
        "keywords": "transcribe sales call, customer interview transcript, product research, gong alternative free",
        "h1": "How to Transcribe a Sales Call or Customer Interview for Product Research",
        "quick_answer": "Transcribe the recording. Tag each section by theme (pricing, onboarding, churn reason). Copy the literal quotes as evidence. Product decisions point to timestamps, not your memory.",
        "faq": [
            {
                "q": "Why not just use Gong or Fathom?",
                "a": "Both are good. Both are $100+/seat/month. If you run a handful of calls a month, transcripts + a simple tagging doc is enough."
            },
            {
                "q": "What themes should I tag for?",
                "a": "Pick 4-6 that matter to your current decision. Starter set: pricing objection, onboarding friction, aha moment, churn reason, feature ask, competitor mentioned."
            },
            {
                "q": "Should I share transcripts with engineering?",
                "a": "Yes — with specific timestamps. “User said X at 14:23” beats a Slack summary. Engineers believe what they heard."
            },
            {
                "q": "How do I respect privacy?",
                "a": "Always get recording consent. Redact last names and company names when sharing outside the research team."
            }
        ],
        "body_html": """
<p>Sales calls and customer interviews are where product strategy gets real. You want the literal words, not a summary.</p>
<h2>The 60-second answer</h2>
<p>Transcribe with <a href=\"/\">TranscriptX</a>. Open a doc with theme columns. Copy the literal quotes into each theme with timestamps. Decisions cite the timestamps.</p>
<h2>Step-by-step</h2>
<h3>1) Transcribe the recording</h3>
<p>Paste the Zoom, Teams, Gong, or Chorus recording link on <a href=\"/\">transcriptx.xyz</a>.</p>
<h3>2) Set up your theme doc</h3>
<p>Before reading, list the 4-6 themes you care about:</p>
<pre><code>- Pricing objection
- Onboarding friction
- Aha moment
- Churn reason
- Competitor mentioned
- Feature request</code></pre>
<h3>3) Read and tag</h3>
<p>As you skim, drop quotes into the matching theme column. Include timestamp and user name (or anonymized ID).</p>
<h3>4) Summarize weekly</h3>
<p>At week’s end, count how many times each theme showed up. That count is your signal — backed up with raw quotes.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Summarizing instead of quoting.</strong> Once you’re paraphrasing, decisions drift from what users said. Use the literal words.</li>
  <li><strong>Skipping consent.</strong> Always confirm recording. Some jurisdictions require two-party consent.</li>
  <li><strong>Raw transcripts in Slack.</strong> Personal data in persistent channels. Redact or share a controlled doc link.</li>
  <li><strong>Waiting for 50 calls.</strong> 5 calls with clear theme patterns beats 50 that you didn’t tag until the end.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to turn an interview into quotes</a>.</li>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label multiple speakers</a>.</li>
  <li><a href=\"/guides/transcribe-zoom-recording\">How to transcribe a Zoom recording</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your call recording link</a>.</p>
""",
    },
    "transcribe-x-spaces-recording": {
        "title": "How to Transcribe a Twitter/X Spaces Recording",
        "description": "Spaces recordings are short-lived and buried inside the X app. Here’s the workflow for grabbing a transcript before the replay expires.",
        "keywords": "transcribe x spaces, twitter spaces transcript, spaces recording to text",
        "h1": "How to Transcribe a Twitter/X Spaces Recording",
        "quick_answer": "Open the Space on x.com, copy the URL, paste on TranscriptX. If the host didn’t enable replay, you’ve missed it — the Space vanished when it ended.",
        "faq": [
            {
                "q": "How long are Spaces recordings available?",
                "a": "30 days if the host enabled replay. If they didn’t, the Space is gone when it ends."
            },
            {
                "q": "Does it work on mobile?",
                "a": "Copy the link from the X app and open TranscriptX in a browser. Desktop is easier for grabbing the URL."
            },
            {
                "q": "Can I transcribe a live Space?",
                "a": "No — we need a completed recording. Wait until the Space ends and the replay is processed (usually a few minutes)."
            },
            {
                "q": "What if the host deleted the recording?",
                "a": "Then it’s gone. X doesn’t restore deleted Spaces."
            }
        ],
        "body_html": """
<p>Twitter/X Spaces are ephemeral. If you want the transcript, grab it before the replay expires.</p>
<h2>The 30-second answer</h2>
<p>Open the Space on <a href=\"https://x.com\" rel=\"nofollow\">x.com</a>, copy the URL, paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Find the Space on X</h3>
<p>Go to the host’s profile. If replay is on, the Space appears pinned near the top or in their posts.</p>
<h3>2) Copy the URL</h3>
<p>URL format is <code>x.com/i/spaces/SPACEID</code>.</p>
<h3>3) Paste on TranscriptX</h3>
<p>Drop the link on <a href=\"/\">transcriptx.xyz</a>. Long Spaces (2-3 hours is common) take proportionally longer.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>No replay enabled.</strong> Some hosts turn off replay. No recovery.</li>
  <li><strong>Replay expired.</strong> 30 days and the URL 404s.</li>
  <li><strong>Protected account host.</strong> We can’t follow anyone.</li>
  <li><strong>Overlapping speakers.</strong> Common on Spaces with 5+ active speakers. Expect some garbled patches.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-multi-speaker-video\">How to label multiple speakers</a>.</li>
  <li><a href=\"/guides/transcribe-webinar-for-blog\">How to turn a Space into a blog post</a>.</li>
  <li><a href=\"/guides/interview-transcript-to-quotes\">How to pull quotes from a Space</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste an X Spaces link</a> now.</p>
""",
    },
    "transcribe-whatsapp-voice-memo": {
        "title": "How to Transcribe a WhatsApp Voice Memo or Voice Note",
        "description": "That 6-minute voice note from your aunt? Get it to text in 30 seconds. Works for personal memos, legal evidence, and journalism source files.",
        "keywords": "transcribe whatsapp voice note, voice memo transcript, voice note to text, whatsapp audio transcript",
        "h1": "How to Transcribe a WhatsApp Voice Memo or Voice Note",
        "quick_answer": "Long-press the voice note in WhatsApp → Share → save to your phone. Upload the file to Google Drive, make the link public, paste on TranscriptX.",
        "faq": [
            {
                "q": "Why upload to Drive first?",
                "a": "WhatsApp voice notes live locally on your phone — no direct share link. Drive is the fastest path to a URL we can fetch."
            },
            {
                "q": "Can I transcribe iPhone Voice Memos the same way?",
                "a": "Yes. Voice Memos are .m4a by default. Share to Drive, paste on TranscriptX."
            },
            {
                "q": "What about Android voice messages?",
                "a": "Same idea. Long-press → Share → save to Files → upload to Drive."
            },
            {
                "q": "Is this legal for recording conversations?",
                "a": "Transcribing a voice memo sent to you is fine. Recording someone secretly depends on local laws (one-party vs two-party consent). Check before you record."
            }
        ],
        "body_html": """
<p>Voice notes are great to receive and impossible to search. Transcription fixes that in under a minute.</p>
<h2>The 30-second answer</h2>
<p>Long-press the WhatsApp voice note → <strong>Share</strong> → save to your phone → upload to <a href=\"https://drive.google.com\" rel=\"nofollow\">Google Drive</a> → make link public → paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step — iPhone</h2>
<h3>1) Long-press the voice note in WhatsApp</h3>
<p>Tap <strong>Share</strong> → <strong>Save to Files</strong> (or share to the Drive app directly).</p>
<h3>2) Upload to Drive, set sharing</h3>
<p>Open Drive, upload the file, tap the file → Share → <strong>Anyone with the link</strong>.</p>
<h3>3) Copy link, paste on TranscriptX</h3>
<p><a href=\"/\">transcriptx.xyz</a> → paste → Transcribe.</p>
<h2>Step-by-step — Android</h2>
<p>Long-press the voice message → Share → pick Drive. Make the link public. Paste on TranscriptX.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Drive link Restricted.</strong> Switch to Anyone with the link.</li>
  <li><strong>WhatsApp export failure.</strong> Very long voice notes can fail on older phones. Update WhatsApp.</li>
  <li><strong>Multiple speakers in one note.</strong> Workflow still works, but you’ll want to label who said what.</li>
  <li><strong>Thick accent or background noise.</strong> Accuracy drops. Try the language retry if auto-detect is off.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-google-drive-video\">How to transcribe a Google Drive video</a>.</li>
  <li><a href=\"/guides/transcribe-iphone-video\">How to transcribe a video on your iPhone</a>.</li>
  <li><a href=\"/guides/transcribe-foreign-language-video\">How to transcribe a voice note in another language</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste the Drive link</a>.</p>
""",
    },
    "transcribe-spotify-podcast": {
        "title": "How to Transcribe a Podcast Episode From Spotify (When There’s No YouTube Version)",
        "description": "Spotify blocks most scrapers. The fix: find the podcast’s RSS feed or Apple Podcasts listing, grab the direct MP3, paste that into TranscriptX.",
        "keywords": "transcribe spotify podcast, spotify episode transcript, spotify to text, podcast transcript no youtube",
        "h1": "How to Transcribe a Podcast Episode From Spotify (When There’s No YouTube Version)",
        "quick_answer": "Spotify itself is locked. Find the episode on Apple Podcasts or the show’s own site — both usually link the raw MP3. Paste the MP3 URL on TranscriptX.",
        "faq": [
            {
                "q": "Why can’t you transcribe Spotify links directly?",
                "a": "Spotify requires authentication for almost every stream, and their DRM blocks bulk download. We’d need your login to play the audio, which we don’t want."
            },
            {
                "q": "What if the show is Spotify-exclusive?",
                "a": "Then there’s no public MP3 and no legal workaround. You’d have to record playback yourself."
            },
            {
                "q": "Where do I find the MP3 URL?",
                "a": "Apple Podcasts pages, the show’s website, Overcast, Pocket Casts. Right-click the audio player and “Copy audio URL”."
            },
            {
                "q": "Spotify podcast video episodes?",
                "a": "Same limitation — Spotify’s video player requires auth. If the show also posts to YouTube (many do), use that."
            }
        ],
        "body_html": """
<p>Spotify is a closed garden for podcasts. The transcript workflow routes around it.</p>
<h2>The 60-second answer</h2>
<p>Find the episode on <a href=\"https://podcasts.apple.com\" rel=\"nofollow\">Apple Podcasts</a>, the show’s website, or Overcast. Find the direct MP3. Paste that URL on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Identify the episode</h3>
<p>Note the show name and episode title.</p>
<h3>2) Find the MP3 URL</h3>
<ul>
  <li><strong>Apple Podcasts</strong> — the player often exposes the MP3 in page source.</li>
  <li><strong>The show’s website</strong> — many embed the raw file.</li>
  <li><strong>Overcast or Pocket Casts</strong> — both often show the direct file URL.</li>
</ul>
<h3>3) Paste the MP3 URL on TranscriptX</h3>
<p>Drop the URL on <a href=\"/\">transcriptx.xyz</a>. Podcast MP3s transcribe cleanly.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Spotify-exclusive show.</strong> No public MP3, no workaround.</li>
  <li><strong>Paid/subscriber-only episode.</strong> Patreon or Substack gates. Download from your own account first.</li>
  <li><strong>Geo-restricted podcast.</strong> Rare, but some CDNs block non-US access.</li>
  <li><strong>Stitched ads.</strong> Dynamic ad insertion is common. Your transcript will include whatever ads the feed served.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-mp3-from-url\">How to transcribe an MP3 podcast from a direct URL</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a podcast into show notes</a>.</li>
  <li><a href=\"/guides/transcribe-soundcloud-track\">How to transcribe a SoundCloud track</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste an MP3 URL</a>.</p>
""",
    },
    "transcribe-iphone-video": {
        "title": "How to Transcribe a Video on Your iPhone (Without an App)",
        "description": "iPhone has built-in transcription for Voice Memos but nothing for video files. Here’s the no-app flow: share sheet → Drive → TranscriptX, in about 60 seconds.",
        "keywords": "transcribe iphone video, iphone video to text, transcribe phone video",
        "h1": "How to Transcribe a Video on Your iPhone (Without an App)",
        "quick_answer": "Open the video in Photos, tap Share → Save to Files or Drive, upload to Google Drive with a public link, paste the link on TranscriptX. No app install.",
        "faq": [
            {
                "q": "Doesn’t iPhone have built-in transcription?",
                "a": "Voice Memos does. Photos (for video) doesn’t. That’s why you route through Drive."
            },
            {
                "q": "What file sizes work?",
                "a": "As long as Drive accepts it (effectively no limit for most users), we can transcribe it."
            },
            {
                "q": "Can I use iCloud Drive instead of Google Drive?",
                "a": "Usually no — iCloud public links gate heavily and often require an Apple ID to open. Google Drive’s “Anyone with the link” is more reliable."
            },
            {
                "q": "What about Dropbox?",
                "a": "Dropbox works. Share a public link with “Can view” access and paste on TranscriptX."
            }
        ],
        "body_html": """
<p>iPhone records great video and gives you zero built-in options for transcribing it. The workaround is quick.</p>
<h2>The 60-second answer</h2>
<p>Video in Photos → <strong>Share</strong> → <strong>Save to Files</strong> (or Drive app) → upload to Google Drive → public link → paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Open the video in Photos</h3>
<p>Tap the video → <strong>Share</strong> (bottom-left).</p>
<h3>2) Save to Files or Drive</h3>
<p>Scroll the share sheet → tap <strong>Save to Files</strong>, or tap the <strong>Drive</strong> app. Drive is faster if you have it.</p>
<h3>3) In Drive, make the link public</h3>
<p>Long-press the file → Share → <strong>Anyone with the link</strong> → Copy link.</p>
<p><em>[Screenshot: Drive iOS Share dialog with Anyone with the link selected]</em></p>
<h3>4) Paste on TranscriptX</h3>
<p>Open Safari → <a href=\"/\">transcriptx.xyz</a> → paste → Transcribe.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Drive link Restricted.</strong> Flip to Anyone with the link.</li>
  <li><strong>iCloud share link.</strong> iCloud often gates past non-Apple browsers. Use Google Drive.</li>
  <li><strong>Huge video (multi-GB).</strong> Upload time is the bottleneck. Let Drive finish syncing first.</li>
  <li><strong>HEIC or oddball codec.</strong> Standard iPhone .mov files work. Unusual re-encodes sometimes don’t.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-google-drive-video\">How to transcribe a Google Drive video</a>.</li>
  <li><a href=\"/guides/transcribe-whatsapp-voice-memo\">How to transcribe a WhatsApp voice note</a>.</li>
  <li><a href=\"/guides/transcribe-instagram-reel-or-story\">How to transcribe an Instagram Reel</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste your Drive link</a> from your iPhone.</p>
""",
    },
    "transcribe-youtube-short": {
        "title": "How to Transcribe a YouTube Short",
        "description": "Shorts often have no captions because they’re too short to auto-caption. TranscriptX handles them the same as any YouTube URL — paste and go.",
        "keywords": "transcribe youtube short, youtube shorts transcript, shorts to text",
        "h1": "How to Transcribe a YouTube Short",
        "quick_answer": "Copy the Short’s URL, paste on TranscriptX. Works the same as a regular YouTube video. Because Shorts are short, transcripts come back in under 10 seconds.",
        "faq": [
            {
                "q": "Why don’t Shorts have captions like regular YouTube?",
                "a": "YouTube often skips auto-captioning very short videos. And creators can’t easily export the ones that do get captioned."
            },
            {
                "q": "Is the URL format different?",
                "a": "Slightly — Shorts use <code>youtube.com/shorts/VIDEO_ID</code>. Paste as-is; we handle both formats."
            },
            {
                "q": "Does it work on private Shorts?",
                "a": "Same rules as any YouTube video: Public and Unlisted work, Private doesn’t."
            },
            {
                "q": "Music-only Shorts?",
                "a": "No speech, no transcript. Expected."
            }
        ],
        "body_html": """
<p>YouTube Shorts are a separate corner of YouTube with their own caption problems. The fix is the same paste-and-go.</p>
<h2>The 15-second answer</h2>
<p>Copy the Short URL, paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Copy the Short URL</h3>
<p>Share → Copy link. URL format: <code>youtube.com/shorts/ABC123</code>.</p>
<h3>2) Paste on TranscriptX</h3>
<p><a href=\"/\">transcriptx.xyz</a> → paste → Transcribe. Under 10 seconds for most.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Private Short.</strong> Same rule as any Private YouTube video.</li>
  <li><strong>Age-restricted.</strong> Adult login required.</li>
  <li><strong>Region-locked.</strong> Blocked outside the creator’s country.</li>
  <li><strong>Music-only.</strong> No spoken content = empty transcript.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-private-youtube-video\">How to transcribe a private or unlisted YouTube video</a>.</li>
  <li><a href=\"/guides/transcribe-tiktok-video\">How to transcribe a TikTok</a>.</li>
  <li><a href=\"/guides/transcribe-instagram-reel-or-story\">How to transcribe an Instagram Reel</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a Short URL</a>.</p>
""",
    },
    "transcribe-reddit-video": {
        "title": "How to Transcribe a Reddit Video Post (v.redd.it)",
        "description": "Reddit-hosted videos (v.redd.it URLs) are notoriously hard because audio and video live in separate files. Here’s the reliable path.",
        "keywords": "transcribe reddit video, v.redd.it transcript, reddit video to text",
        "h1": "How to Transcribe a Reddit Video Post (v.redd.it)",
        "quick_answer": "Copy the Reddit post URL (the reddit.com/r/... one, not the v.redd.it one). Paste on TranscriptX. We handle Reddit’s split audio/video format behind the scenes.",
        "faq": [
            {
                "q": "Why is Reddit video weird?",
                "a": "Reddit stores video and audio as separate files on v.redd.it. Naive scrapers grab the silent video and miss the audio. We fetch and merge both."
            },
            {
                "q": "Should I copy the post URL or the v.redd.it URL?",
                "a": "Post URL is more reliable. It gives us the context needed to find the audio. v.redd.it URLs sometimes work, sometimes don’t."
            },
            {
                "q": "Crossposts?",
                "a": "Yes, if the original post still exists. If the original was deleted, the crosspost video may be inaccessible."
            },
            {
                "q": "Private subreddit posts?",
                "a": "No. Private subs require membership. Our servers aren’t members."
            }
        ],
        "body_html": """
<p>Reddit videos break a lot of transcript tools because Reddit splits audio and video into separate files. Ours doesn’t.</p>
<h2>The 30-second answer</h2>
<p>Copy the <strong>post URL</strong> (the <code>reddit.com/r/...</code> one), not the v.redd.it URL. Paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Get the post URL</h3>
<p>Click the post’s timestamp or title. Copy the URL from the address bar. Format: <code>reddit.com/r/SUB/comments/ID/SLUG</code>.</p>
<h3>2) Paste on TranscriptX</h3>
<p><a href=\"/\">transcriptx.xyz</a> → paste. If the post has a v.redd.it video, we’ll fetch both tracks and merge.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Using the v.redd.it URL directly.</strong> Sometimes works, sometimes 403s. Use the post URL.</li>
  <li><strong>Video without audio track.</strong> Screen recordings or GIFs repackaged as video are truly silent. No audio = empty transcript.</li>
  <li><strong>Deleted post.</strong> If the post or video was removed, it’s gone.</li>
  <li><strong>NSFW-gated community.</strong> Some subs require account-age or karma. We don’t have an account.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-tiktok-video\">How to transcribe a TikTok</a>.</li>
  <li><a href=\"/guides/transcribe-youtube-short\">How to transcribe a YouTube Short</a>.</li>
  <li><a href=\"/guides/transcribe-mp3-from-url\">How to transcribe from a direct audio URL</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a Reddit post URL</a>.</p>
""",
    },
    "transcribe-mp3-from-url": {
        "title": "How to Transcribe an MP3 Podcast File From a Direct URL",
        "description": "If you have the raw MP3 URL — from a podcast RSS feed, Overcast, Pocket Casts, or the show’s website — you can transcribe it without downloading.",
        "keywords": "transcribe mp3 url, podcast mp3 transcript, audio url to text, rss feed transcript",
        "h1": "How to Transcribe an MP3 Podcast File From a Direct URL",
        "quick_answer": "Paste the MP3 URL on TranscriptX. We fetch and transcribe — no download step. Works for any public .mp3 or .m4a URL.",
        "faq": [
            {
                "q": "Where do I find the direct MP3 URL?",
                "a": "RSS feeds, Apple Podcasts pages, Overcast, Pocket Casts, and most show websites."
            },
            {
                "q": "Other audio formats?",
                "a": "Yes — .m4a, .wav, .ogg, .opus. Anything Whisper can decode."
            },
            {
                "q": "MP3s behind paywalls?",
                "a": "If the URL requires authentication, we can’t fetch it. Download on your own account and upload to a public storage link."
            },
            {
                "q": "File size limits?",
                "a": "We transcribe multi-hour podcast files routinely. Processing time scales with length."
            }
        ],
        "body_html": """
<p>If you have the raw MP3 URL, you have the simplest transcription job possible. No UI to click through.</p>
<h2>The 15-second answer</h2>
<p>Paste the MP3 URL on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step — finding the MP3</h2>
<ul>
  <li><strong>Show’s RSS feed.</strong> Every open podcast has one. The <code>&lt;enclosure url=\"...\"&gt;</code> in each episode is the MP3.</li>
  <li><strong>Apple Podcasts web page.</strong> Play the episode → right-click audio → Copy audio URL.</li>
  <li><strong>Overcast / Pocket Casts.</strong> Share episode → copy the web link → inspect for the MP3.</li>
  <li><strong>Show’s website.</strong> Many embed the player directly; right-click, copy the source URL.</li>
</ul>
<h2>Step-by-step — transcribing</h2>
<p>Drop the URL on <a href=\"/\">transcriptx.xyz</a>. Hit Transcribe.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>URL behind auth.</strong> Patreon, Substack, premium feeds. Can’t fetch.</li>
  <li><strong>Expired CDN URL.</strong> Some hosts expire direct links after a while. Grab a fresh one.</li>
  <li><strong>Dynamic ad insertion.</strong> Your transcript will include whatever ads the feed served.</li>
  <li><strong>DRM-protected audio.</strong> Audible and some commercial products. Not accessible.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-spotify-podcast\">How to transcribe a Spotify podcast</a>.</li>
  <li><a href=\"/guides/transcribe-soundcloud-track\">How to transcribe a SoundCloud track</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a podcast into show notes</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste an MP3 URL</a>.</p>
""",
    },
    "transcribe-soundcloud-track": {
        "title": "How to Transcribe a SoundCloud Track or DJ Mix",
        "description": "SoundCloud doesn’t export captions and their stream URLs are messy. Paste the track URL into TranscriptX — we handle the fetch. Good for DJ mixes, interview snippets, and liner notes.",
        "keywords": "transcribe soundcloud, soundcloud to text, dj mix transcript, soundcloud track transcript",
        "h1": "How to Transcribe a SoundCloud Track or DJ Mix",
        "quick_answer": "Copy the SoundCloud track URL (soundcloud.com/artist/track-name), paste on TranscriptX. Works on public tracks and mixes. Private tracks with secret links usually work too.",
        "faq": [
            {
                "q": "Why transcribe a DJ mix?",
                "a": "Liner notes, track-ID from spoken intros, Boiler Room interview snippets. DJs and music journalists use this a lot."
            },
            {
                "q": "Private tracks?",
                "a": "Usually — if the track has a “secret link” you can share, we can fetch it. If it requires a SoundCloud login, we can’t."
            },
            {
                "q": "SoundCloud Go+ paywalled tracks?",
                "a": "Require a subscription. Preview-only URLs give you a short transcript of the preview."
            },
            {
                "q": "Instrumental or lyric-heavy music?",
                "a": "Instrumentals have nothing to transcribe. Lyric-heavy music works, but Whisper isn’t tuned for song lyrics — results are rougher than spoken word."
            }
        ],
        "body_html": """
<p>SoundCloud won’t export captions. DJ mixes and podcast-style shows are still a goldmine of spoken content if you can extract it.</p>
<h2>The 30-second answer</h2>
<p>Copy the track URL from SoundCloud, paste on <a href=\"/\">TranscriptX</a>.</p>
<h2>Step-by-step</h2>
<h3>1) Get the track URL</h3>
<p>On soundcloud.com, open the track. Copy the URL from the browser. Format: <code>soundcloud.com/artist/track-name</code>.</p>
<h3>2) Paste on TranscriptX</h3>
<p><a href=\"/\">transcriptx.xyz</a>. DJ mixes and long episodes take proportionally longer.</p>
<h2>Common things that break</h2>
<ul>
  <li><strong>Private track without a secret link.</strong> Can’t fetch.</li>
  <li><strong>SoundCloud Go+ paywalled.</strong> Requires a subscription.</li>
  <li><strong>Purely instrumental music.</strong> Nothing to transcribe.</li>
  <li><strong>Lyrics over heavy beats.</strong> Whisper is tuned for speech, not lyrics. Expect rougher output on sung music.</li>
</ul>
<h2>Related guides</h2>
<ul>
  <li><a href=\"/guides/transcribe-mp3-from-url\">How to transcribe an MP3 from a direct URL</a>.</li>
  <li><a href=\"/guides/transcribe-spotify-podcast\">How to transcribe a Spotify podcast</a>.</li>
  <li><a href=\"/guides/youtube-video-to-show-notes\">How to turn a mix into show notes</a>.</li>
</ul>
<h2>Try it</h2>
<p>3 free transcripts a month. <a href=\"/\">Paste a SoundCloud link</a>.</p>
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


# ── MCP server ────────────────────────────────────────────────
#
# Subdomain mounting requires SERVER_NAME to be set so Flask knows what to
# match against. We only set it in production (Railway sets PORT) — locally
# we mount the MCP routes on the default host instead, which lets you hit
# them at http://localhost:5000/ via the same Flask app for testing.
from mcp_server import register_mcp_routes  # noqa: E402

_MCP_SUBDOMAIN = "mcp"
if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("FLASK_PROD"):
    app.config["SERVER_NAME"] = os.environ.get("FLASK_SERVER_NAME", "transcriptx.xyz")
    register_mcp_routes(app, subdomain=_MCP_SUBDOMAIN)
else:
    # Dev: mount on default host. Hit at http://localhost:5000/?token=...
    # Note: this conflicts with the homepage route, so dev testing requires
    # /etc/hosts mapping for mcp.transcriptx.local + FLASK_SERVER_NAME env var
    # if you want a true subdomain-style local test. For quick smoke tests,
    # set FLASK_PROD=1 and add `127.0.0.1 mcp.transcriptx.xyz` to /etc/hosts.
    pass


# ── Strip MCP tokens from access logs ─────────────────────────
class _StripTokenFilter(logging.Filter):
    """Werkzeug logs include the full URL including ?token=. Redact it."""
    _re = re.compile(r"token=[^\s&\"'<>]+")
    def filter(self, record):
        if record.args:
            record.args = tuple(
                self._re.sub("token=***", a) if isinstance(a, str) else a
                for a in record.args
            )
        if isinstance(record.msg, str):
            record.msg = self._re.sub("token=***", record.msg)
        return True


_werkzeug_logger = logging.getLogger("werkzeug")
_werkzeug_logger.addFilter(_StripTokenFilter())


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