# MCP Server v0.1 — Implementation plan

Tactical breakdown of the work in [PRD.md](PRD.md). Phased so each phase is independently testable.

## Phase 1 — Foundation: token model + auth

**Goal:** A user can generate an MCP token via DB call, and the server can validate it.

### Files touched

- `database.py` — schema + helpers
- `seo_catalog.py` — unchanged (MCP doesn't affect SEO surfaces)

### DB schema addition

```python
db.execute("""
    CREATE TABLE IF NOT EXISTS mcp_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        token_prefix TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        last_used_at TEXT,
        revoked_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
db.execute("CREATE INDEX IF NOT EXISTS idx_mcp_tokens_user ON mcp_tokens(user_id)")
db.execute("CREATE INDEX IF NOT EXISTS idx_mcp_tokens_hash ON mcp_tokens(token_hash) WHERE revoked_at IS NULL")
```

### Helper functions

```python
def generate_mcp_token(user_id) -> dict:
    """Returns {token: 'tx_personal_xxx', token_id: 1, prefix: 'tx_per_'}.
    Token shown once. Hash stored in DB."""

def validate_mcp_token(raw_token) -> int | None:
    """Returns user_id if token is valid + not revoked. Updates last_used_at."""

def revoke_mcp_token(token_id, user_id) -> bool:
    """Sets revoked_at = now. Returns True on success, False if not user's token."""

def list_user_mcp_tokens(user_id) -> list:
    """Returns list of {id, prefix, created_at, last_used_at, revoked_at}."""
```

### Token format

`tx_personal_<32-char-base32>` — Stripe-style. Readable in logs without leaking the secret. The `tx_personal_` prefix doubles as a future namespace if we later add `tx_oauth_`, `tx_service_`, etc.

`token_prefix` stored separately = first 12 chars (`tx_personal_`) + first 4 chars of the random part. Used in the settings UI to remind the user which token is which (e.g., `tx_personal_a3f1...`).

### Done when

- DB migration runs cleanly on existing DBs (idempotent CREATE TABLE IF NOT EXISTS)
- Unit-level: generate → validate → revoke → validate (returns None) all work
- Token never appears in logs

## Phase 2 — Settings UI

**Goal:** A logged-in user can visit a settings page, click Generate, get a token shown once, and revoke when done.

### Routes

```python
@app.route("/account/mcp")
def account_mcp_page():
    """Settings page — lists active tokens, generate button."""

@app.route("/api/mcp/generate-token", methods=["POST"])
def api_mcp_generate_token():
    """Creates new token. Returns {status: 'ok', token, token_id, prefix}."""

@app.route("/api/mcp/revoke-token", methods=["POST"])
def api_mcp_revoke_token():
    """Revokes by token_id. Returns {status: 'ok'}."""
```

### Template

`templates/account_mcp.html`:

- Page header: "MCP / AI Connector"
- Short explainer (3-4 lines): what MCP is, why someone'd use it
- Active tokens list (one row each: prefix, created date, last-used date, Revoke button)
- "Generate new token" button
- Generated-token modal/section:
  - Shown once after generate
  - Full token + ready-to-paste URL
  - Copy buttons for both
  - Warning: "This token won't be shown again. Save it now."

### Done when

- User can generate token → see it once → close → see only the prefix in the list
- Generated URL is `https://mcp.transcriptx.xyz/?token=tx_personal_xxx`
- Revoke removes from the list and renders the token invalid

## Phase 3 — Protocol server

**Goal:** An MCP client connects to `mcp.transcriptx.xyz`, lists 3 tools, and can call them.

### Dependencies

```
mcp >= 1.0.0    # Anthropic's official Python SDK
```

Add to `requirements.txt`.

### Subdomain config

In `app.py` (only in production):

```python
if os.environ.get("FLASK_ENV") == "production":
    app.config["SERVER_NAME"] = "transcriptx.xyz"
```

### Routes (subdomain="mcp")

```python
mcp_bp = Blueprint("mcp", __name__, subdomain="mcp")

@mcp_bp.route("/", methods=["GET", "POST"])
def mcp_handler():
    """All MCP traffic — JSON-RPC over HTTP. Auth via token query/header."""
    user_id = _get_mcp_user_id_from_request()
    if not user_id:
        return _json_rpc_error(...), 401
    # Dispatch via mcp SDK
```

### Token resolution

```python
def _get_mcp_user_id_from_request():
    raw = request.args.get("token") or _bearer_token(request.headers.get("Authorization", ""))
    if not raw:
        return None
    return validate_mcp_token(raw)
```

### Tool implementations

Each tool wraps existing logic. No new transcription code.

```python
async def tool_transcribe_url(user_id, url, language=None, model=None):
    """Internally calls the same path as /api/extract."""
    # 1. Validate URL, normalize language
    # 2. Check + deduct credits (use_credit_for_user)
    # 3. Call process_url(url, model=model, language=language)
    # 4. Log to transcript_log (log_transcript_attempt)
    # 5. Return {log_id, url, language, transcript, duration_seconds, credits_remaining}

async def tool_list_recent_transcripts(user_id, limit=20):
    """SELECT against transcript_log table."""

async def tool_get_transcript_by_id(user_id, log_id):
    """SELECT one log entry, verify user_id ownership, return transcript text."""
```

### Logging hygiene

Werkzeug's default access log includes the full URL. Add a log filter that strips `?token=...`:

```python
class StripTokenFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, "msg") and "token=" in str(record.msg):
            record.msg = re.sub(r"token=[\\w_]+", "token=***", str(record.msg))
        return True
```

### Done when

- A test MCP client (e.g., `mcp-cli` or Claude Desktop with manual config) can connect to `mcp.transcriptx.xyz/?token=...` and list the 3 tools
- `transcribe_url` against a real YouTube URL returns a transcript and increments credits_used
- Invalid token → JSON-RPC error response with appropriate code
- Access logs show `token=***` not the raw token

## Phase 4 — Setup docs

**Goal:** A user can find a single page that tells them how to configure their AI client.

### Routes

```python
@app.route("/mcp/setup")
def mcp_setup_page():
    """Public page — no auth needed. Per-client config snippets."""
```

### Content

Tabbed UI (or stacked sections — simpler):

- **Claude Desktop** — JSON snippet for `claude_desktop_config.json`
- **Cursor** — JSON snippet for Cursor's MCP settings
- **ChatGPT** — instructions for ChatGPT's MCP integration
- **Continue.dev** — config block
- **Cline** — config block

Each snippet uses `https://mcp.transcriptx.xyz/?token=YOUR_TOKEN` as the placeholder. Link prominently to the `/account/mcp` page where they generate one.

### Done when

- `/mcp/setup` renders cleanly with copy buttons on each config block
- Copy → paste into the actual client → tools appear
- Linked from settings page and footer

## Cross-phase concerns

### Local testing

Subdomain blueprints require `SERVER_NAME` to be set, which breaks plain `localhost:5000` access. For local dev:

- Add to `/etc/hosts`: `127.0.0.1 transcriptx.local mcp.transcriptx.local`
- Set `FLASK_SERVER_NAME=transcriptx.local:5000` env var
- Hit `http://transcriptx.local:5000/` for web, `http://mcp.transcriptx.local:5000/?token=...` for MCP

This is documented in a one-paragraph comment at the SERVER_NAME config line.

### Cloudflare / Railway routing

`mcp.transcriptx.xyz` needs DNS pointing to the Railway service. Two options:

- Add a CNAME record on Cloudflare → same Railway target as `transcriptx.xyz`
- Use Railway custom domains (add `mcp.transcriptx.xyz` to the same service)

Either works. Cloudflare CNAME is simpler if DNS is already there.

### Phased rollout

- Phase 1 + 2 + 3 land together as a single PR. Without all three you can't usefully test.
- Phase 4 (setup docs) can be a follow-up PR if Phase 3 is taking longer.
- After ship: monitor `mcp_tokens.last_used_at` to see token activity. If usage looks healthy after week 2, write up the announcement and submit to Anthropic's gallery.

## Estimated effort (calendar weeks)

- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 4-6 days (the SDK has subtle quirks; budget time for protocol-correctness debugging)
- Phase 4: 1 day
- Total: ~1.5-2 weeks for one focused engineer

## What can go wrong

- **MCP SDK version drift.** Anthropic ships changes regularly. Pin a known-good version in `requirements.txt`. Re-test before any pin bump.
- **Subdomain config breaking dev.** Mitigation above (`/etc/hosts` + env var).
- **Token leak via logs.** The `StripTokenFilter` covers Werkzeug; double-check we don't print the URL anywhere else (no f-strings logging the full URL in our handlers).
- **First Cloudflare cache of an auth-error response.** Set `Cache-Control: no-store` on all `/mcp/*` responses to be safe.
- **Bad credit accounting** — make sure exactly one credit is deducted per successful `transcribe_url` and zero on failure. Reuse the existing `use_credit_for_user` + `refund_credit_for_user` flow; do not write new credit logic.
