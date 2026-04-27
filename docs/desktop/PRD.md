# Desktop App — PRD (minimal)

One-page product doc. Deliberately short. Decisions and scope, not implementation details.

## Problem

Users with local video/audio files have to upload them to Google Drive (or similar), make the link public, paste on the web app. Three extra steps. The `upload-audio-file-transcript` help page in `seo_catalog.py` is literally a doc explaining this workaround — proof the UX is broken.

Direct web file upload isn't on the near-term roadmap because it means our servers eat GBs of bandwidth + storage per user. The cost doesn't pencil out.

## Solution (what we build)

A thin desktop client that handles the heavy upload locally:

1. User drags a video or audio file into the app.
2. App extracts audio locally with bundled ffmpeg (shrinks a 2 GB video to ~30 MB audio).
3. App uploads the audio to our existing TranscriptX API.
4. Server runs the normal Groq + logging flow.
5. Transcript appears in the app + is saved to the user's account history.

**This is a thick client for our existing pipeline.** No new transcription stack. No local Whisper. Audio still leaves the device. The pitch is *"skip the Drive step,"* not *"private local transcription."*

## Core user flow

- Log in with existing TranscriptX account (same email/password as web).
- Drag file onto the window, or click to pick.
- Progress bar: extracting → uploading → transcribing.
- Transcript shown with copy / export as `.txt` / `.srt` / `.vtt`.
- Language retry (reuse the F8 pattern) available inline.
- Transcript appears in the user's web history immediately.

## Scope (v0.5 ship)

In:
- macOS Apple Silicon + Intel, one signed + notarized build.
- Drag-and-drop local file transcription (video or audio).
- ffmpeg bundled for audio extraction.
- Auth via existing web account.
- History sync with the web DB.
- Export `.txt` / `.srt` / `.vtt`.
- Language picker + free retry flow (port the F8 UX).

Out (v0.5):
- URL pasting. Web does it. Could add later if usage data says it matters.
- Windows / Linux builds.
- System-audio capture (menu-bar recorder).
- Local Whisper inference.
- iOS / iPad companion.
- Real-time / live captioning.

## Pricing

Bundled with existing Pro tier. Free-plan users get the same 3/month cap enforced against the same credit counter. No new SKU. No new billing code.

Rationale: the desktop app doesn't cost us more per transcript than the web does (same Groq call), so there's no reason to price it separately. Using the existing counter means one source of truth.

## Server-side change needed

One new endpoint: `POST /api/transcribe-upload`. Accepts a multipart audio file (not a URL). Same auth + credit checks as `/api/transcribe`. Same Groq flow. Same response shape. Same logging (set `url` field to `desktop://<filename>` or similar so history shows file name).

Everything else on the server is unchanged.

## Success criteria

- **Week 2 post-launch:** 20%+ of existing Pro users have downloaded + signed in at least once.
- **Month 1:** average Pro user runs ≥3 transcripts/month through the desktop app (sign of habit forming).
- **Month 3:** measurable conversion lift in free → Pro, specifically in users who landed on the `upload-audio-file-transcript` help page or any of the F1-adjacent guides (Zoom, Loom, Teams, iPhone). If these groups convert no better than the baseline, the desktop app didn't solve the problem we thought.

## Kill criteria

- If month-3 Pro conversion is flat vs baseline AND desktop-app usage is under 10% of Pro MAUs, the thesis was wrong. Sunset the app and bring file upload to the web instead.
- If Mac App Store or notarization friction exceeds what two weeks of engineering effort can fix, we direct-ship only (no App Store listing). Not a kill — just a scope contraction.

## Open questions (need answers before build starts)

1. **File-only or file + URL?** PRD assumes file-only. Changing this adds 1-2 weeks of scope for yt-dlp bundling and signing headaches. Default: file-only.
2. **Mac-only or cross-platform from day 1?** PRD assumes Mac-only for v0.5. Windows is a v1.0 decision based on v0.5 signal.
3. **Tauri or Electron?** Not a product question but informs timeline. Defaulting to Tauri (smaller binary, reuse of existing web UI components).
4. **Auto-update infra?** Sparkle (Mac-standard) or roll our own? Defaulting to Sparkle.

## API reference (what exists today)

All endpoints are on `https://transcriptx.xyz`, auth is **cookie-based Flask session** today. Every JSON endpoint returns `{"status": "ok" | "error", ...}`. Error responses carry an `error` string and an appropriate HTTP status code.

### Auth + account

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/signup` | `{email, password, referral_code?}` | Sends OTP, returns `{status: "ok", step: "verify"}`. Blocks disposable email domains. |
| POST | `/api/verify` | `{email, code}` | Verifies OTP. Logs user in on success. |
| POST | `/api/resend-code` | `{email}` | Resends OTP. |
| POST | `/api/login` | `{email, password}` | Sets session cookie. Returns `{status: "ok", plan}` or `{status: "verify"}` if unverified. |
| POST | `/api/logout` | — | Clears session. |
| POST | `/api/forgot-password/request` | `{email}` | Sends reset OTP. |
| POST | `/api/forgot-password/confirm` | `{email, code, password}` | Resets password. |
| GET  | `/api/me` | — | Current user + credits. Returns `{logged_in, user_id, email, plan_name, credits, plan}`. |
| GET  | `/api/me/referral` | — | Referral code + lifetime stats. Auth required. |

### Transcription + content

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/extract` | `{url, model?, language?}` | URL-based transcription. Deducts 1 credit. Returns `{status, log_id, language, transcript, segments, words, url, views, likes, comments, duration_formatted, ...}`. Refunds credit on infra-side failures. |
| POST | `/api/retranscribe` | `{log_id, language}` | Free retry with forced language. One retry per `log_id` ever. Auth required. |
| POST | `/api/rate-transcript` | `{log_id, rating}` | Rating is `1` (thumbs up) or `-1` (thumbs down). |
| POST | `/api/extract-preview` | `{url}` | Anonymous 60-second preview. Used for the no-signup first transcript flow. |

### What the desktop app needs (to be added)

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/transcribe-upload` | multipart `audio` file + `filename`, `language?`, `model?` | New. Accepts an audio file directly instead of a URL. Same auth + credit checks as `/api/extract`. Same response shape. Logs with `url = desktop://<filename>` so history stays unified. |

### Auth open question for desktop

Session cookies work fine in a Tauri webview (we can share cookies with `transcriptx.xyz` via the system cookie store). Electron does this cleanly too. If we want a cleaner separation — or if we ship a native Swift/Windows client later — we'd add a bearer-token flow: one new endpoint (`POST /api/token` trading email+password for a long-lived token) and a middleware that accepts either cookie or `Authorization: Bearer <token>` on every protected route.

Decision: defer the bearer-token flow to v1.0. v0.5 uses cookies.

### Not used by desktop (skip)

`/api/download-video`, `/api/download-segment`, `/api/featurebase-token`, `/api/profile-links` — either admin-flavored, feature-flagged, or specific to the web product. Desktop ignores them.

## What this doc is not

- Not a spec. No wireframes, no data models. Those come after scope is locked.
- Not a roadmap. No week-by-week plan until we agree on the shape here.
- Not a moat play. This doesn't build a defensible advantage on its own — it closes a specific UX gap that's costing conversions today. If we later want a real moat (privacy, offline, local-first), that's a separate v1.0+ plan.

---

**One-line version:** Small Mac app. Drag file in. Audio gets extracted locally, uploaded to our existing API, transcript comes back. Same account, same pricing, no Drive workaround.
