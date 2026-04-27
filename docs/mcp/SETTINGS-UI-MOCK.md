# MCP settings UI mock

ASCII sketch of the page at `/account/mcp`. Voice and visual style match existing settings pages.

## State 1: First visit (no tokens yet)

```
┌─────────────────────────────────────────────────────────────────────┐
│  TRANSCRIPTX                              [home] [pricing] [logout] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ACCOUNT  ›  MCP / AI Connector                                     │
│                                                                     │
│  Use TranscriptX inside Claude Desktop, Cursor, ChatGPT, and        │
│  other AI clients. Generate a token, paste the URL into your        │
│  client's MCP config, then say "transcribe this video" inside       │
│  the AI of your choice. → Setup guide                               │
│                                                                     │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ACTIVE TOKENS                                                      │
│                                                                     │
│  No tokens yet. Generate one to get started.                        │
│                                                                     │
│  ┌─────────────────────────┐                                        │
│  │ + Generate MCP token    │                                        │
│  └─────────────────────────┘                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## State 2: Just generated a token (shown once)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ACCOUNT  ›  MCP / AI Connector                                     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ ⚠  Save this now — we won't show it again.                   │  │
│  │                                                               │  │
│  │ Your full MCP URL:                                            │  │
│  │ ┌─────────────────────────────────────────────────────┐ ┌──┐ │  │
│  │ │ https://mcp.transcriptx.xyz/?token=tx_personal_...  │ │📋│ │  │
│  │ └─────────────────────────────────────────────────────┘ └──┘ │  │
│  │                                                               │  │
│  │ Token only (if your client takes them separately):           │  │
│  │ ┌─────────────────────────────────────────────────────┐ ┌──┐ │  │
│  │ │ tx_personal_a3f1b2c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8     │ │📋│ │  │
│  │ └─────────────────────────────────────────────────────┘ └──┘ │  │
│  │                                                               │  │
│  │ Paste this into Claude Desktop, Cursor, or whatever client    │  │
│  │ you use. → Setup guide for each client                        │  │
│  │                                                               │  │
│  │ [ I've saved it, close ]                                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## State 3: With one active token

```
┌─────────────────────────────────────────────────────────────────────┐
│  ACCOUNT  ›  MCP / AI Connector                                     │
│                                                                     │
│  Use TranscriptX inside Claude Desktop, Cursor, ChatGPT, and        │
│  other AI clients. → Setup guide                                    │
│                                                                     │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ACTIVE TOKENS                                                      │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  tx_personal_a3f1...                                          │  │
│  │  Created 2026-04-27  ·  Last used 2 hours ago                 │  │
│  │                                                    [ Revoke ] │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────┐                                        │
│  │ + Generate MCP token    │                                        │
│  └─────────────────────────┘                                        │
│                                                                     │
│  Why might I want a second token? Some users want one for           │
│  Claude Desktop, another for Cursor, so they can revoke per-client. │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## State 4: Revoke confirmation (inline, no modal)

```
┌───────────────────────────────────────────────────────────────┐
│  tx_personal_a3f1...                                          │
│  Created 2026-04-27  ·  Last used 2 hours ago                 │
│                                                               │
│  Revoking will immediately stop this token from working.      │
│  Your AI clients will need a new token.                       │
│                                                               │
│                                  [ Cancel ]   [ Revoke now ]  │
└───────────────────────────────────────────────────────────────┘
```

## Voice rules in this UI

- Plain English. No "leverage your AI workflow" or "seamless connector experience."
- Direct. "Save this now — we won't show it again." Not "Please ensure you have securely stored this credential before navigating away from this page."
- Honest. The "Why might I want a second token?" line addresses the real question rather than pretending users won't have one.

## States not in v0.1

- Per-token labels ("for Claude", "for Cursor"). v1.0+.
- Token rotation policies (auto-rotate every N days). Out of scope.
- Per-token usage stats (calls last 7 days, etc.). Nice-to-have, post-launch.
- Per-token rate limits. Out of scope.
