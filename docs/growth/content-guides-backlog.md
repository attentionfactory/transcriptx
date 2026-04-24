# Content Guides Backlog

The list of how-to guides we should write, ranked by search intent and workflow pain. Replaces the SEO-fluff style of the current `GUIDES_CONTENT` in `app.py` ("manual vs AI transcription", "repurpose video into SEO post" — generic, nobody searches for them).

## Principles for every guide

- **H1 = the exact problem the user Googled.** No cute copy.
- **60-second answer up top.** Before any preamble.
- **One screenshot per step.** If a step has no screenshot, it's probably skippable.
- **"Common things that break" section at the end.** This is the moat — competitors won't write it.
- **Internal link to the most relevant supported-site page and pricing.**
- **No "compounds", "long-tail", "mid-funnel", or "workflow optimization".** Write how a smart friend would explain it.

## Tier 1 — High-intent, under-served (write first)

Someone typed this into Google today and got a weak answer. Ranking here converts.

1. **How to transcribe a Google Drive video (without downloading it)**
   Share → copy link → paste. Screenshot the Drive share dropdown — that's where people get stuck. Covers Zoom recordings auto-saved to Drive.
2. **How to transcribe a Zoom recording without paying for Zoom AI Companion**
   Two flows: cloud recording → share link → paste; local mp4 → Drive → share → paste.
3. **How to get the transcript of a TikTok video**
   Public, private/unlisted, captions ≠ transcript. Honest about what works.
4. **How to transcribe a private or unlisted YouTube video**
   Which privacy settings work, which don't, unlisted-link workaround.
5. **How to transcribe an Instagram Reel or Story**
   Reels work; Stories are hard (ephemeral + auth-gated). Screen-record workaround.
6. **How to transcribe a Loom video**
   Loom has captions but no clean export. Share link → paste.
7. **How to transcribe a Vimeo video (public, password-protected, or private)**
   Three privacy modes covered. Vimeo's own captions are paywalled on Plus+.
8. **How to transcribe a Microsoft Teams meeting recording**
   Teams transcripts need admin enablement. SharePoint/OneDrive share-link workaround.
9. **How to transcribe a Facebook video or live stream**
   Public posts, Watch videos, saved Lives. FB has auto-captions but no export.
10. **How to transcribe a Twitch VOD or clip**
    Streamers for YouTube reuploads, sponsor reports, copyright disputes.

## Tier 2 — Real workflows

Someone is already a power user. These deepen activation and retention.

11. **How to turn a 2-hour interview into quotes you can actually use**
    Post-transcript: Ctrl-F, timestamp jumps, speaker labels, quotes into a doc.
12. **How to transcribe a lecture for study notes (and turn it into flashcards)**
    Panopto/Echo360/Zoom lecture → transcript → Anki/Quizlet paste.
13. **How to turn a YouTube video into clean show notes with timestamps**
    Podcaster workflow. Transcript → chapter markers → bullet summary → publish.
14. **How to transcribe a video in a different language (and translate it)**
    Use Whisper auto-detect + our language override + free retry. Then translate.
15. **How to transcribe a video with multiple speakers and label who said what**
    Diarization. Honest: AI labels are ~80% right, here's how to fix in 2 min.
16. **How to transcribe a webinar or conference talk for blog repurposing**
    Recording link → transcript → article + LinkedIn post + clip captions.
17. **How to transcribe a sales call or customer interview for product research**
    Gong/Fathom alternative flow. Themes, tags, evidence quotes.

## Tier 3 — Long-tail evergreen

Lower volume but easy to rank and genuinely helpful.

18. **How to transcribe a Twitter/X Spaces recording**
    Underserved. Save → share → transcribe.
19. **How to transcribe an audio file from WhatsApp or a voice memo**
    Massive search volume ("how to transcribe voice note"). Journalists and lawyers search this.
20. **How to transcribe a podcast episode from Spotify (when there's no YouTube version)**
    Spotify blocks most scrapers. RSS/Apple Podcasts workaround, or direct MP3 from the show's site.
21. **How to transcribe a video on your iPhone (without an app)**
    iPhone has Voice Memos transcription but not for video. Share sheet → Drive → paste.
22. **How to transcribe a YouTube Short**
    Separate guide from regular YouTube; Shorts often have no captions.
23. **How to transcribe a Reddit video post (v.redd.it)**
    Reddit-hosted videos are notoriously hard. Clear ranking win.
24. **How to transcribe an MP3 podcast file from a direct URL**
    Apple/Overcast/Pocket Casts share links.
25. **How to transcribe a SoundCloud track or DJ mix**
    Niche but loyal — DJs, music journalists, liner-note writers.

## Highest leverage subset

If we only wrote five next, these solve problems the user can't easily fix elsewhere and the search intent is unambiguous:

- #1 Google Drive
- #6 Loom
- #8 Microsoft Teams
- #14 Language / translate
- #21 iPhone

## Template for each guide

```
H1: "How to transcribe a [thing]"
60-second answer (paragraph)
Step 1: get the link (screenshot)
Step 2: paste into TranscriptX (screenshot)
Step 3: grab the output (formats we offer)
Common things that break:
  - permission errors (what to toggle)
  - auth-gated content (when it fails and what to do instead)
  - language detection (link to language override retry)
Related guides (2–3 internal links)
CTA: try free (3/month)
```

## Guides to retire or rewrite

Currently in `GUIDES_CONTENT` at [app.py:2276](../../app.py):

- `repurpose-video-into-seo-post` — generic marketing fluff, no specific Google intent. Retire or rewrite as "How to turn a YouTube video into a blog post" (= #13 above).
- `manual-vs-ai-transcription` — nobody searches this comparison with buying intent. Retire.
- `youtube-transcript-generator`, `video-to-transcript`, `download-youtube-transcript`, `audio-to-transcript`, `youtube-video-to-transcript` — these are landing-page-style, not guides. Consider moving them out of `/guides/` into the main SEO landing set, and reserving `/guides/` for actual step-by-step tutorials.

## Kill criteria

- Any guide that doesn't hit 50 impressions/mo in GSC within 90 days of publish → rewrite the H1 or retire.
- Any guide with CTR <1% after 90 days at 500+ impressions → meta title/description is wrong, rewrite.
- Guide bundle as a whole: if none of the top 10 convert to a signup within 6 months, the guide strategy is wrong and we should shift to comparison pages + tool pages only.
