# MCP Server — PRD (minimal)

One-page product doc. Decisions and scope, not implementation details. Modeled on `docs/desktop/PRD.md`.

## Problem

AI-power users live inside Claude Desktop, Cursor, ChatGPT, and similar agents. When they want a transcript, they have to leave the AI, paste a URL into TranscriptX, copy the result, paste it back into the conversation. Three tool-switches per task.

The web product has no presence inside the AI client surfaces where these users actually work. As MCP-based connector galleries grow (Anthropic's Connectors directory, OpenAI's MCP support, Cursor's tools panel), absence from those surfaces is missed distribution.

## Solution (what we build)

A remote MCP server at **`mcp.transcriptx.xyz`** that exposes TranscriptX as tools any MCP-compatible AI client can call. Users authenticate with a personal token, configure their AI client once, then say "transcribe this YouTube video" inside their AI of choice and get the transcript back into the conversation.

This is **a thin protocol adapter on top of the existing API**, not a new product. The `transcribe_url` tool internally calls the same `/api/extract` pipeline. Same Groq, same logging, same credit counter, same DB.

## Core user flow

1. User opens TranscriptX → Account Settings → "MCP Token" section.
2. Clicks **Generate token**. App shows the token once with the full MCP URL: `https://mcp.transcriptx.xyz/?token=tx_personal_abc123xyz`.
3. User copies the URL into their AI client's MCP config (Claude Desktop, Cursor, ChatGPT, etc.).
4. AI client connects, lists available tools (`transcribe_url`, `list_recent_transcripts`, `get_transcript_by_id`).
5. User says: *"Transcribe this and pull out the three strongest quotes: <URL>"*. The AI calls `transcribe_url`, gets the text back, summarizes inline.
6. Transcript is logged to the user's history — visible on the web in `/profile-links` and via `list_recent_transcripts` in any future MCP session.

## Scope (v0.1 ship)

In:

- Subdomain `mcp.transcriptx.xyz` routed to the same Flask app via subdomain blueprint.
- Personal-token auth — accepts `?token=...` query param OR `Authorization: Bearer ...` header. Same token, same DB lookup.
- New `mcp_tokens` table (one token per user, regenerable, revocable).
- New settings UI on TranscriptX for generating + revoking the token.
- Three MCP tools:
  - `transcribe_url(url, language?, model?)` — wraps `/api/extract`
  - `list_recent_transcripts(limit?)` — wraps existing `transcript_log` SELECT
  - `get_transcript_by_id(log_id)` — wraps existing log fetch
- Setup docs page covering Claude Desktop, Cursor, ChatGPT, Continue, Cline.

Out (v0.1):

- OAuth 2.0 + DCR. Defer to v0.5 if/when needed for "Featured" connector gallery placement.
- `retry_transcript_language` tool. Add if usage data shows it matters.
- Multiple labeled tokens per user (e.g., one for Claude, one for Cursor). Single token covers all clients in v0.1; add labels if users complain.
- Hour-rate caps. Add monitoring instead; ship the cap reactively if abuse surfaces.
- `transcriptx://transcript/{id}` MCP resources. The 3 tools cover history adequately for v0.1.
- Streaming partial transcripts.
- Submit to Anthropic's Featured Connectors gallery. Apply once OAuth is in place.

## Pricing

Same credit counter as web + desktop. No new SKU, no new billing code.

- Free plan: 3/month cap, shared across web + desktop + MCP calls.
- Pro plan: unlimited, shared across all surfaces.

Rationale: an MCP `transcribe_url` call costs us the same Groq cycles as a web `/api/extract` call. Pricing parity = single source of truth = no billing surprises.

## Server-side changes needed

1. **New DB table `mcp_tokens`**:

   ```
   id INTEGER PK
   user_id INTEGER FK → users(id)
   token_hash TEXT (we store the hash, not the token)
   token_prefix TEXT (first 8 chars, for display in settings UI)
   created_at TEXT
   last_used_at TEXT NULLABLE
   revoked_at TEXT NULLABLE
   ```

   One row per active token per user. Hash stored, not the raw token.

2. **New Flask blueprint** registered with `subdomain="mcp"`. `SERVER_NAME` set to `transcriptx.xyz` so the routing works.

3. **New endpoints on the MCP subdomain**:

   - `GET /` — MCP server discovery (initialization handshake per protocol spec).
   - `POST /` — JSON-RPC tool calls (the protocol's request endpoint).

   Both auth via token (URL query or Authorization header). Both reuse existing `_get_current_user_by_id()` after token resolution.

4. **New settings UI** on the web (likely `/account` or similar) — Generate / Revoke / Show Token buttons. Token shown once at generation; subsequent visits show only the prefix + revoke button.

5. **Strip `?token=` from access logs** — security hygiene. Easy Flask logging filter.

6. **Use the official MCP Python SDK** (`mcp` package from Anthropic). Don't roll the JSON-RPC + handshake protocol by hand — the spec has subtle requirements that the SDK handles correctly.

## MCP tools reference (v0.1)

### `transcribe_url`

Transcribe a public video or audio URL. Deducts 1 credit on success.

**Input:**
```json
{
  "url": "https://youtube.com/watch?v=...",
  "language": "en",         // optional ISO-639-1 code; auto-detect if omitted
  "model": "whisper-large-v3-turbo"  // optional; defaults to turbo
}
```

**Output:**
```json
{
  "log_id": 12345,
  "url": "https://youtube.com/watch?v=...",
  "language": "en",
  "transcript": "...",
  "duration_seconds": 1234,
  "credits_remaining": 47
}
```

Errors mirror `/api/extract` (auth required, no credits, invalid URL, transcription failed). Returned as MCP error responses with structured `code` and `message` fields.

### `list_recent_transcripts`

Returns the calling user's recent transcript history.

**Input:** `{"limit": 20}` (optional, defaults to 20, max 100)

**Output:** array of `{log_id, url, language, status, created_at, duration_seconds}` — no transcript text (use `get_transcript_by_id` for that).

### `get_transcript_by_id`

Returns the full transcript for a log_id the user owns.

**Input:** `{"log_id": 12345}`

**Output:** same shape as `transcribe_url` output, minus `credits_remaining`. Returns 403 if the log_id belongs to a different user.

## Success criteria

- **Week 2 post-launch:** 100+ users have generated an MCP token.
- **Month 1:** average MCP-active user makes ≥2 `transcribe_url` calls/week (sign of habit forming, not just curiosity).
- **Month 3:** measurable conversion lift in free → Pro from MCP-active users vs baseline. If MCP-active users hit the 3/mo cap and convert at the same rate as web-only users, MCP isn't accelerating — it's just an alternate surface.

## Kill criteria

- If month-3 MCP-active conversion is flat vs baseline AND active MCP users < 5% of monthly actives, the distribution thesis was wrong. Ramp down support, mark as legacy, focus elsewhere.
- If Anthropic's Connectors gallery rejects URL-token-only servers AND we don't see meaningful organic growth via word-of-mouth, prioritize OAuth in v0.5 to unblock the listing.

## Open questions (need answers before build)

1. **Settings UI placement.** Existing `/account` page? New `/settings/mcp` route? Defaulting to a new dedicated section on the main account page.
2. **Token format.** `tx_personal_<random>` (Stripe-style) vs UUID vs JWT. Defaulting to Stripe-style — readable, scannable in logs, hard to misread.
3. **Token rotation policy.** Auto-rotate after N days, or only on user request? Defaulting to user-request only.
4. **Anthropic gallery submission.** Submit at v0.1 (URL-token) and accept that we won't be Featured, or wait for v0.5 (OAuth)? Defaulting to "submit at v0.1, accept the placement we get."

## API reference (what exists today, reused by MCP)

The MCP server doesn't add new TranscriptX-side endpoints — it wraps existing ones. See [docs/desktop/PRD.md](../desktop/PRD.md#api-reference-what-exists-today) for the full API list. The MCP-relevant subset:

| Existing endpoint | MCP tool that wraps it |
|---|---|
| `POST /api/extract` | `transcribe_url` |
| `GET /api/me` (for credit count) | embedded in `transcribe_url` response |
| `GET /transcript/<log_id>` (or DB lookup) | `get_transcript_by_id` |
| `GET` on `transcript_log` table | `list_recent_transcripts` |

Internal token validation logic is new (`mcp_tokens` table lookup). Everything downstream is existing.

## What this doc is not

- Not a spec. No JSON-RPC payloads, no Flask handler signatures, no full DB DDL. Those come after scope is locked.
- Not a roadmap. No week-by-week plan until we agree on this shape.
- Not a moat. Single tool wrapping a public API isn't defensible alone — it's a distribution play. The moat is the existing transcription quality + content + brand. MCP is the way users find that.

---

**One-line version:** Subdomain MCP server. User pastes a personal-token URL into Claude/Cursor/ChatGPT MCP config. AI gets three tools to transcribe URLs and look up history. Same account, same pricing, no OAuth in v0.1.
