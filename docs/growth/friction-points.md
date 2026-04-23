# Friction Points

A running log of places the product makes the user do extra work, fail silently, or hit a wall. Sourced from FAQs, error messages, help pages, and the guide backlog.

**Operating idea:** every guide we have to write is a confession of a missing feature. Every error message that ends with "try again later" is a place users churn. Every help page titled "What if X?" is a feature request in disguise.

Each friction point: **what hurts → where it shows up → product fix → severity.**

## High severity (likely losing signups or paid conversion)

### F1. URL-only — can't upload local files
- **Friction:** users with a recording on their laptop have to upload it to Drive, share, copy link, paste. 3 extra steps before our product starts.
- **Where:** every "Zoom recording", "Teams recording", "Loom", "iPhone video" guide in [content-guides-backlog.md](content-guides-backlog.md). Help page exists at `seo_catalog.py` HELP_PAGES `upload-audio-file-transcript` lines 1821-1899 — it's literally a doc explaining the workaround.
- **Fix:** accept direct file upload (start with 500 MB cap). Closes ~40% of the guide backlog at once.
- **Severity:** high.

### F2. Private YouTube videos fail without telling the user why
- **Friction:** user pastes a private/unlisted link, gets a generic error or silent failure, no path forward.
- **Where:** `seo_catalog.py` HELP_PAGES `private-video-transcript` (1672-1750). Generic error in [app.py:657](app.py:657) `return jsonify({"status": "error", "error": str(e)}), 400` — exposes raw exception strings.
- **Fix:** detect privacy errors specifically; return "this video is private — change to Unlisted or sign in to YouTube" with a link to the help page. Long-term: YouTube OAuth so users can transcribe their own private videos.
- **Severity:** high.

### F3. Out-of-credits error has no in-line upgrade path
- **Friction:** "No credits remaining. Upgrade your plan!" — but the JSON response is just text. The frontend has to know to render an upgrade button.
- **Where:** [app.py:670](app.py:670) `jsonify({"status": "error", "error": "No credits remaining. Upgrade your plan!"})`. No `upgrade_url` field, no `credits_needed` field.
- **Fix:** structured error: `{error, upgrade_url, current_credits, plan, suggested_plan}`. Frontend renders a one-click upgrade.
- **Severity:** high.

### F4. Zoom/Teams/Meet recordings have no native integration
- **Friction:** the most common business use case (transcribe a meeting recording) is also the highest-friction path. Cloud recording → find it → share → copy link → paste.
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #2, #8.
- **Fix:** OAuth integrations with Zoom and Microsoft Graph. Pull cloud recordings directly. Phase 1 = Zoom only (it's the largest share).
- **Severity:** high.

### F5. Generic 400 errors expose raw Python exception strings
- **Friction:** [app.py:657](app.py:657), [app.py:736](app.py:736), [app.py:875](app.py:875) all do `error: str(e)`. Users see things like "HTTP Error 403: Forbidden" or yt-dlp internal messages they can't act on.
- **Fix:** error classifier that maps common downstream errors to user-readable messages with recovery actions ("this site requires login", "this video is age-restricted", "this URL format isn't recognized — paste the watch URL not the share URL").
- **Severity:** high.

## Medium severity (losing activation)

### F6. Google Drive folder URLs vs file URLs
- **Friction:** user shares a folder link instead of a file link → fails. They don't know the difference.
- **Where:** `seo_catalog.py` HELP_PAGES `google-drive-transcript-link` (1598-1670).
- **Fix:** detect folder URLs client-side in the paste box, show "this looks like a folder — open the file first and copy that link" before they even submit.
- **Severity:** medium.

### F7. Region-locked videos fail with no signal
- **Friction:** geo-blocked content fails; user thinks the product is broken.
- **Where:** `seo_catalog.py` HELP_PAGES `region-locked-video-transcript` (1751-1820).
- **Fix:** detect geo-block in the response, show "this video is region-locked from our servers (US) — try the original platform or a mirror".
- **Severity:** medium.

### F8. Language detection is silent — users don't know retry exists
- **Friction:** Whisper guesses wrong on accented or multilingual audio. The free retry feature exists ([app.py:740](app.py:740) `/api/retranscribe`) but the UI only surfaces it as a "retry with different language" button after the fact, if at all.
- **Fix:** show detected language prominently on the result with a "wrong language? retry free" inline button. Tooltip: "Whisper guessed [X] — if that's wrong, retry once free".
- **Severity:** medium.

### F9. Preview limit error is a dead end
- **Friction:** [app.py:817](app.py:817) `"Preview limit reached. Try again later or log in for full extraction."` — "try again later" is the worst CTA.
- **Fix:** inline signup form right there. The user is already engaged; the cost of forcing them to wait is they leave.
- **Severity:** medium.

### F10. Free-tier reset is invisible
- **Friction:** user runs out of 3 free transcripts on day 5, doesn't come back. No reset notification on day 1 of next month.
- **Where:** no email cron found for monthly reset reminders. Activation doc proposed it ([activation-retention.md](activation-retention.md) #4).
- **Fix:** day-before-reset email with "your 3 free transcripts reset tomorrow".
- **Severity:** medium.

### F11. Loom requires manual share-link copy
- **Friction:** Loom is the dominant async-video tool in remote work; we have no Loom-specific path.
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #6.
- **Fix:** Loom OAuth (they have an API). Pull recordings directly from the user's Loom library.
- **Severity:** medium.

### F12. Speaker labels are ~80% accurate, no edit UI
- **Friction:** multi-speaker transcripts have wrong labels. User has to copy to a doc and find/replace manually.
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #15.
- **Fix:** in-product speaker label editor — click "Speaker 1" → rename to "Sarah", applies to all instances. Cheap to build, high perceived quality bump.
- **Severity:** medium.

### F13. Instagram Stories work intermittently with no honest signal
- **Friction:** Stories are auth-gated and ephemeral. Sometimes succeed, often fail. User assumes our product is unreliable.
- **Where:** `seo_catalog.py` HELP_PAGES `instagram-story-transcript` (1900-1961).
- **Fix:** detect Story URLs and show "Stories are unreliable to transcribe (Instagram blocks most attempts) — screen-record to your camera roll, then upload" *before* they paste, not after.
- **Severity:** medium.

### F14. Rate-limit errors say "try again later" with no time
- **Friction:** [app.py:566](app.py:566) `"Too many requests. Try again later."` — when? 1 minute? 1 hour?
- **Fix:** include `retry_after` seconds in the response, render a countdown in the UI.
- **Severity:** medium.

## Low severity (polish)

### F15. iPhone has no native path
- **Friction:** mobile-share workflow is "share to Drive, then go back to TranscriptX in Safari" — clunky.
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #21.
- **Fix:** iOS Shortcut as a v0 (no app needed) — ship via shortcut gallery. Native app is the v1.
- **Severity:** low.

### F16. YouTube Shorts fall through the YouTube logic
- **Friction:** Shorts often lack captions; the YouTube-tuned extractor sometimes returns empty.
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #22.
- **Fix:** detect Shorts URLs, route to audio-extraction path directly instead of trying captions first.
- **Severity:** low.

### F17. No transcript history dashboard for free users
- **Friction:** free users get a transcript, copy it, leave. No reason to come back.
- **Where:** [activation-retention.md](activation-retention.md) #5 proposed it.
- **Fix:** a minimal "your past transcripts" page — even for free users (last 30 days).
- **Severity:** low.

### F18. No batch URL paste
- **Friction:** podcaster wants to transcribe last 10 episodes — has to paste, wait, paste, wait.
- **Where:** referenced as a Pro+ feature in [pricing-experiments.md](pricing-experiments.md) #4.
- **Fix:** paste 10 URLs at once, queue them, email when all done. Could be a Pro-only feature to drive upgrade.
- **Severity:** low.

### F19. Spotify is unsupported but listed nowhere as such
- **Friction:** users assume "1000+ sites" includes Spotify. It doesn't (Spotify blocks scrapers).
- **Where:** [content-guides-backlog.md](content-guides-backlog.md) #20 admits the workaround.
- **Fix:** explicit "Spotify isn't supported, here's how to find the same episode elsewhere" page. Honesty > confusion.
- **Severity:** low.

## Cross-cutting themes

Reading these together, three patterns emerge:

1. **The product is a URL parser, not a file processor.** F1, F4, F6, F11, F15 all share this DNA. Resolving them requires either accepting files or building integrations.
2. **Errors are honest with the server but cryptic to the user.** F2, F3, F5, F7, F9, F13, F14 are all "the backend knows what's wrong, the user doesn't". A unified error classifier is the highest-leverage cross-cutting fix.
3. **The product doesn't bring users back.** F10, F17, F18 are about session #2, not session #1. Activation is fine; retention has no system behind it.

## How we'd prioritize

If we ship one thing per week for the next month:

- **Week 1:** F5 (error classifier) — touches half the other items, low engineering cost.
- **Week 2:** F8 (language retry surfacing) — already built, just needs UI promotion.
- **Week 3:** F1 (file upload, behind a Pro flag to limit infra spend) — closes the largest guide cluster.
- **Week 4:** F3 (structured upgrade error) — highest direct revenue impact.

Then re-evaluate. The Zoom integration (F4) is the next big rock but takes longer than a week.

## How we'd know we got it wrong

- Ship F5 → if support tickets about "it just failed" don't drop in 30 days, the classifier isn't catching the right errors.
- Ship F1 → if file uploads stay <5% of total transcripts after 60 days, users actually wanted URLs and the friction was imagined.
- Ship F4 → if Zoom integration usage <3% of paid users after 90 days, meetings aren't our wedge after all and we should stop chasing them.
