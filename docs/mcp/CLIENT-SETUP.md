# Setting up TranscriptX in your AI client

Replace `YOUR_TOKEN` with the token from `/account/mcp`. The full URL form is `https://mcp.transcriptx.xyz/?token=YOUR_TOKEN`.

## Claude Desktop

Open `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows). Add to the `mcpServers` block:

```json
{
  "mcpServers": {
    "transcriptx": {
      "url": "https://mcp.transcriptx.xyz/?token=YOUR_TOKEN"
    }
  }
}
```

Restart Claude Desktop. You'll see a small tool icon next to the input — TranscriptX is connected. Try: *"Transcribe this and summarize the three main points: <YouTube URL>"*

## Cursor

Open Settings → MCP → Add new server. Use:

- Name: `TranscriptX`
- Type: `streamableHttp` (or `http`, depending on your Cursor version)
- URL: `https://mcp.transcriptx.xyz/?token=YOUR_TOKEN`

Save. Cursor will connect and show the tools in the chat panel's tool list.

## ChatGPT (with MCP support)

In ChatGPT's connector settings, add a new MCP server:

- URL: `https://mcp.transcriptx.xyz/?token=YOUR_TOKEN`
- Auth: None (token is in the URL)

Save. ChatGPT will pick up the tools and surface them inside conversations.

## Continue.dev

In your Continue config (typically `~/.continue/config.json`), add:

```json
{
  "mcpServers": {
    "transcriptx": {
      "url": "https://mcp.transcriptx.xyz/?token=YOUR_TOKEN"
    }
  }
}
```

Reload Continue.

## Cline

Open Cline settings → MCP Servers. Add:

```json
{
  "transcriptx": {
    "url": "https://mcp.transcriptx.xyz/?token=YOUR_TOKEN"
  }
}
```

## Authorization header (alternative)

If your client doesn't accept the token in the URL, use:

- URL: `https://mcp.transcriptx.xyz/`
- Header: `Authorization: Bearer YOUR_TOKEN`

Both are equivalent. The token validates against the same DB row.

## Verifying the connection

Once configured, ask the AI: *"What tools do you have available from TranscriptX?"*

You should see three:

- `transcribe_url` — transcribe any public video or audio URL
- `list_recent_transcripts` — your recent transcript history
- `get_transcript_by_id` — fetch the full text of a past transcript

If the tools don't show, check:

1. Token is current (not revoked) — visit `/account/mcp` to confirm
2. URL is exact (`https://mcp.transcriptx.xyz/?token=...`, no extra slashes)
3. Client supports the streamable-HTTP MCP transport (most do as of 2026)

## Common things that break

- **"Connection refused" or 401.** Token is wrong, expired, or revoked. Generate a new one.
- **"Tools not appearing" but no error.** Restart your AI client fully. Some clients cache the tool list per-session.
- **"Credit limit reached" when calling `transcribe_url`.** Same monthly cap as the web product. Upgrade to Pro for unlimited, or wait for the monthly reset.
- **The transcript came back wrong.** Use `list_recent_transcripts` to get the log_id, then ask the AI to retry with a specific language. (`retry_transcript_language` tool will be added in v0.5; for now, transcribe again and pick the language explicitly.)
