"""
mcp_server.py — Streamable-HTTP MCP server for TranscriptX.

Exposes TranscriptX as tools any MCP-compatible AI client can call.
v0.1 surface: 3 tools, personal-token auth, single Flask app via subdomain blueprint.

Runs on `mcp.transcriptx.xyz` in production; locally hits whatever host is
configured via SERVER_NAME (see app.py).

Auth flow:
- Token comes via `?token=...` query param OR `Authorization: Bearer ...` header.
- validate_mcp_token() returns user_id (or None for invalid/revoked).
- Each tool call runs as that user with the same credit/limit logic as the web.

Protocol: JSON-RPC 2.0 over HTTP per the MCP spec. We implement the minimum
required surface — initialize, tools/list, tools/call, ping — without the
official mcp Python SDK to avoid an extra deploy dependency in v0.1. The
SDK is the right move once we add OAuth and resources in v0.5+.
"""

import json
import logging
import re
from datetime import datetime
from flask import Blueprint, Response, request, jsonify

from database import (
    validate_mcp_token,
    get_user_by_id,
    use_credit_for_user,
    refund_credit_for_user,
    log_transcript_attempt,
    get_transcript_log,
    effective_entitlement,
    PLANS,
)
from transcribe import process_url


log = logging.getLogger(__name__)


# ── Protocol constants ────────────────────────────────────────────────────

# MCP spec version we support. If a client requests something newer, we still
# respond using ours — clients are expected to negotiate down.
PROTOCOL_VERSION = "2024-11-05"

SERVER_INFO = {
    "name": "transcriptx",
    "version": "0.1.0",
}

SERVER_CAPABILITIES = {
    "tools": {"listChanged": False},
}

# Tool definitions exposed to clients via tools/list.
TOOL_DEFINITIONS = [
    {
        "name": "transcribe_url",
        "description": (
            "Transcribe a public video or audio URL. Returns the transcript "
            "text, detected language, and a log_id for later retrieval. "
            "Deducts 1 credit per successful call against the user's plan."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Public URL of the video or audio to transcribe (https only).",
                },
                "language": {
                    "type": "string",
                    "description": "Optional ISO-639-1 language code (e.g. 'en', 'es'). Omit to auto-detect.",
                },
                "model": {
                    "type": "string",
                    "enum": ["whisper-large-v3-turbo", "whisper-large-v3"],
                    "description": "Optional model override. Defaults to whisper-large-v3-turbo.",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_recent_transcripts",
        "description": (
            "Return the user's recent transcript history (newest first). "
            "Returns metadata only — use get_transcript_by_id for full text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Max number of entries to return (1-100, default 20).",
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    },
    {
        "name": "get_transcript_by_id",
        "description": (
            "Fetch the full transcript for a previously-completed log_id. "
            "Only works for log_ids belonging to the calling user."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "log_id": {
                    "type": "integer",
                    "description": "ID of the transcript log entry (returned by transcribe_url).",
                },
            },
            "required": ["log_id"],
        },
    },
]


# ── JSON-RPC helpers ──────────────────────────────────────────────────────

def _rpc_result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_error(req_id, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


# Standard JSON-RPC error codes per spec.
RPC_PARSE_ERROR = -32700
RPC_INVALID_REQUEST = -32600
RPC_METHOD_NOT_FOUND = -32601
RPC_INVALID_PARAMS = -32602
RPC_INTERNAL_ERROR = -32603


# ── Auth ──────────────────────────────────────────────────────────────────

_BEARER_RE = re.compile(r"^Bearer\s+(.+)$", re.IGNORECASE)


def _get_request_token():
    """Pull the MCP token from the request — query param or Authorization header."""
    # Query param wins (it's how we tell users to set up the URL).
    q = request.args.get("token", "").strip()
    if q:
        return q
    auth = request.headers.get("Authorization", "")
    m = _BEARER_RE.match(auth.strip())
    if m:
        return m.group(1).strip()
    return None


def _resolve_user():
    """Return (user_dict, error_response_tuple).

    On success, user_dict has the same shape as _get_current_user() output —
    so downstream tool code can reuse credit + plan logic without changes.
    """
    raw = _get_request_token()
    if not raw:
        return None, ("Missing token. Pass ?token=... or Authorization: Bearer ...", 401)
    user_id = validate_mcp_token(raw)
    if not user_id:
        return None, ("Invalid or revoked token", 401)
    db_user = get_user_by_id(user_id)
    if not db_user:
        return None, ("User no longer exists", 401)

    ent = effective_entitlement(db_user)
    plan_key = ent["effective_plan"]
    plan = PLANS.get(plan_key, PLANS["free"])
    credits = plan["credits"] - db_user["credits_used"] if plan["credits"] != -1 else -1
    if plan["credits"] != -1 and credits < 0:
        credits = 0

    return ({
        "logged_in": True,
        "user_id": user_id,
        "email": db_user["email"],
        "plan": plan_key,
        "plan_name": plan["name"],
        "credits": credits,
    }, None)


# ── Tool implementations ──────────────────────────────────────────────────

# Mirror of app.py's _normalize_language behavior. Local so we don't import
# from app.py (circular).
import re as _re
_LANG_RE = _re.compile(r"^[a-z]{2}$")
_SUPPORTED_LANGS = {
    "en", "es", "fr", "de", "pt", "it", "ja", "ko", "zh", "ru",
    "ar", "hi", "nl", "pl", "tr", "sv", "da", "no", "fi", "cs",
    "uk", "vi", "th", "id", "ms", "he", "ro", "el", "hu", "bg",
    "ca", "fa", "ta", "ur", "bn", "te", "mr", "gu", "kn", "ml",
    "tl", "sw", "af", "sk", "sr", "hr", "lt", "lv", "et", "sl",
}


def _normalize_language(raw):
    if raw is None:
        return None
    code = str(raw).strip().lower()
    if code in ("", "auto"):
        return None
    if not _LANG_RE.match(code):
        raise ValueError("language must be a 2-letter ISO-639-1 code")
    if code not in _SUPPORTED_LANGS:
        raise ValueError(f"language '{code}' is not supported")
    return code


def tool_transcribe_url(user, args):
    """Wraps the same flow as POST /api/extract."""
    url = (args.get("url") or "").strip()
    if not url:
        return _tool_error("url is required")
    if not url.startswith("https://"):
        return _tool_error("URL must start with https://")

    try:
        language = _normalize_language(args.get("language"))
    except ValueError as e:
        return _tool_error(str(e))

    model = args.get("model") or "whisper-large-v3-turbo"
    if model not in ("whisper-large-v3-turbo", "whisper-large-v3"):
        model = "whisper-large-v3-turbo"

    user_id = user["user_id"]
    email = user.get("email", "")

    # Credit gate
    if user["credits"] != -1 and user["credits"] <= 0:
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return _tool_error(
            "No credits remaining on your plan. Upgrade or wait for the monthly reset.",
            data={"current_plan": user.get("plan_name"), "upgrade_url": "https://transcriptx.xyz/pricing"},
        )
    if not use_credit_for_user(user_id):
        log_transcript_attempt(user_id, email, url, "error_no_credits", credits_used=0)
        return _tool_error("No credits remaining on your plan.")

    result = process_url(url, model=model, language=language)
    if result.get("status") == "error":
        if result.get("error_kind") == "user_input":
            log_transcript_attempt(
                user_id, email, url, "error_user_input", credits_used=1,
                requested_language=language,
            )
            return _tool_error(result.get("error", "Transcription failed"), data={"credit_kept": True})
        else:
            refund_credit_for_user(user_id)
            log_transcript_attempt(
                user_id, email, url, "error", credits_used=0,
                requested_language=language,
            )
            return _tool_error(result.get("error", "Transcription failed"))

    log_id = log_transcript_attempt(
        user_id, email, url, "success", credits_used=1,
        requested_language=language,
        detected_language=result.get("language"),
    )

    payload = {
        "log_id": log_id,
        "url": url,
        "language": result.get("language"),
        "transcript": result.get("transcript", ""),
        "duration_seconds": result.get("duration"),
        "credits_remaining": user["credits"] - 1 if user["credits"] != -1 else -1,
    }
    return _tool_text(payload)


def tool_list_recent_transcripts(user, args):
    limit = args.get("limit") or 20
    try:
        limit = max(1, min(100, int(limit)))
    except (TypeError, ValueError):
        return _tool_error("limit must be an integer between 1 and 100")

    from database import get_db
    with get_db() as db:
        rows = db.execute(
            """SELECT id, url, status, credits_used, created_at, requested_language, detected_language
               FROM transcript_logs
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user["user_id"], limit),
        ).fetchall()
        items = [
            {
                "log_id": r["id"],
                "url": r["url"],
                "status": r["status"],
                "credits_used": r["credits_used"],
                "created_at": r["created_at"],
                "language": r["detected_language"] or r["requested_language"],
            }
            for r in rows
        ]
    return _tool_text({"transcripts": items, "count": len(items)})


def tool_get_transcript_by_id(user, args):
    log_id = args.get("log_id")
    try:
        log_id = int(log_id)
    except (TypeError, ValueError):
        return _tool_error("log_id must be an integer")

    log_row = get_transcript_log(log_id, user["user_id"])
    if not log_row:
        return _tool_error("Transcript not found or not yours", data={"log_id": log_id})

    # transcript_logs doesn't store the full text — only metadata. The
    # transcript text lives in process_url's response and was passed to the
    # caller at the time. Re-fetching after the fact is not currently
    # supported on the server side, so we surface what we have honestly.
    payload = {
        "log_id": log_id,
        "url": log_row.get("url"),
        "status": log_row.get("status"),
        "language": log_row.get("detected_language") or log_row.get("requested_language"),
        "created_at": log_row.get("created_at"),
        "note": (
            "Transcript text isn't stored server-side — only metadata. "
            "If you need the full text, retranscribe with transcribe_url. "
            "This will be added in a future version."
        ),
    }
    return _tool_text(payload)


# ── Tool dispatcher ───────────────────────────────────────────────────────

TOOLS = {
    "transcribe_url": tool_transcribe_url,
    "list_recent_transcripts": tool_list_recent_transcripts,
    "get_transcript_by_id": tool_get_transcript_by_id,
}


def _tool_text(payload):
    """Wrap a JSON-serializable payload in MCP tool-result text content."""
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
        "isError": False,
    }


def _tool_error(message, data=None):
    payload = {"error": message}
    if data is not None:
        payload["data"] = data
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "isError": True,
    }


# ── JSON-RPC method dispatcher ────────────────────────────────────────────

def _handle_initialize(req_id, params, user):
    return _rpc_result(req_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": SERVER_CAPABILITIES,
        "serverInfo": SERVER_INFO,
    })


def _handle_tools_list(req_id, params, user):
    return _rpc_result(req_id, {"tools": TOOL_DEFINITIONS})


def _handle_tools_call(req_id, params, user):
    name = (params or {}).get("name")
    arguments = (params or {}).get("arguments") or {}
    if not name:
        return _rpc_error(req_id, RPC_INVALID_PARAMS, "Missing tool name")
    fn = TOOLS.get(name)
    if not fn:
        return _rpc_error(req_id, RPC_INVALID_PARAMS, f"Unknown tool: {name}")
    try:
        result = fn(user, arguments)
        return _rpc_result(req_id, result)
    except Exception as e:
        log.exception("tool '%s' raised", name)
        return _rpc_error(req_id, RPC_INTERNAL_ERROR, "Tool execution failed", {"detail": str(e)[:200]})


def _handle_ping(req_id, params, user):
    return _rpc_result(req_id, {})


METHODS = {
    "initialize": _handle_initialize,
    "tools/list": _handle_tools_list,
    "tools/call": _handle_tools_call,
    "ping": _handle_ping,
}

# Notifications (no response expected). We accept and discard.
NOTIFICATIONS = {"notifications/initialized", "notifications/cancelled"}


# ── Blueprint registration ────────────────────────────────────────────────

def register_mcp_routes(app, *, subdomain="mcp"):
    """Mount the MCP server.

    Pass subdomain=None to register on the default host (handy for local dev
    where SERVER_NAME isn't configured).
    """
    bp_kwargs = {"subdomain": subdomain} if subdomain else {}
    bp = Blueprint("mcp", __name__, **bp_kwargs)

    @bp.route("/", methods=["GET", "POST", "OPTIONS"])
    def mcp_root():
        # CORS preflight for browser-based MCP clients (rare but possible).
        if request.method == "OPTIONS":
            return _cors_response("")

        # Auth applies to both GET (capability discovery) and POST (RPC).
        user, err = _resolve_user()
        if err:
            msg, code = err
            return _cors_response(jsonify({"error": msg}), status=code)

        if request.method == "GET":
            # Some clients GET / for a basic readiness/info check.
            return _cors_response(jsonify({
                "name": SERVER_INFO["name"],
                "version": SERVER_INFO["version"],
                "protocolVersion": PROTOCOL_VERSION,
                "transport": "http+jsonrpc",
                "tools": [t["name"] for t in TOOL_DEFINITIONS],
            }))

        # POST: JSON-RPC payload
        try:
            body = request.get_json(force=True, silent=False)
        except Exception:
            return _cors_response(jsonify(_rpc_error(None, RPC_PARSE_ERROR, "Parse error")), status=400)

        # Single request or batch
        if isinstance(body, list):
            responses = [r for r in (_dispatch(item, user) for item in body) if r is not None]
            return _cors_response(jsonify(responses))
        else:
            response = _dispatch(body, user)
            if response is None:
                # Notification — return 204 No Content per JSON-RPC convention
                return _cors_response("", status=204)
            return _cors_response(jsonify(response))

    app.register_blueprint(bp)


def _dispatch(rpc_request, user):
    """Process one JSON-RPC request. Returns dict or None (for notifications)."""
    if not isinstance(rpc_request, dict):
        return _rpc_error(None, RPC_INVALID_REQUEST, "Request must be an object")
    if rpc_request.get("jsonrpc") != "2.0":
        return _rpc_error(rpc_request.get("id"), RPC_INVALID_REQUEST, "Must be jsonrpc 2.0")
    method = rpc_request.get("method")
    if not method or not isinstance(method, str):
        return _rpc_error(rpc_request.get("id"), RPC_INVALID_REQUEST, "Missing method")
    if method in NOTIFICATIONS:
        return None
    handler = METHODS.get(method)
    if not handler:
        return _rpc_error(rpc_request.get("id"), RPC_METHOD_NOT_FOUND, f"Method not found: {method}")
    try:
        return handler(rpc_request.get("id"), rpc_request.get("params") or {}, user)
    except Exception as e:
        log.exception("RPC handler '%s' raised", method)
        return _rpc_error(rpc_request.get("id"), RPC_INTERNAL_ERROR, "Internal error", {"detail": str(e)[:200]})


def _cors_response(body, status=200):
    """Most MCP clients are server-side, but CORS keeps browser-based ones happy."""
    if isinstance(body, Response):
        resp = body
        resp.status_code = status
    else:
        resp = Response(body if isinstance(body, str) else "", status=status)
        if not isinstance(body, str):
            resp = body
            resp.status_code = status
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Cache-Control"] = "no-store"
    return resp
