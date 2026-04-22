import re
import subprocess
from datetime import datetime, timezone
from functools import lru_cache


HEAD_TERM_PAGES = {
    "youtube-transcript-generator": {
        "path": "/youtube-transcript-generator",
        "slug": "youtube-transcript-generator",
        "title": "YouTube Transcript Generator — Fast AI Transcript | TranscriptX",
        "description": "Generate accurate YouTube transcripts in minutes. Paste a URL, preview free, then export clean transcript text for content, research, and SEO.",
        "h1": "YouTube Transcript Generator",
        "intro": "Turn any public YouTube video into accurate, editable transcript text. Paste a URL, preview output, then extract full text when ready.",
        "keyword": "youtube transcript generator",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "faq": [
            {"q": "Does this work with YouTube Shorts?", "a": "Yes, Shorts URLs are supported as long as the video is publicly accessible."},
            {"q": "Can I get timestamps?", "a": "Yes, TranscriptX returns segment and word-level timestamps when available."},
        ],
    },
    "download-youtube-transcript": {
        "path": "/download-youtube-transcript",
        "slug": "download-youtube-transcript",
        "title": "Download YouTube Transcript — Copy, Export, and Repurpose | TranscriptX",
        "description": "Download a clean YouTube transcript from any public video URL. Ideal for content repurposing, summaries, and SEO writing workflows.",
        "h1": "Download YouTube Transcript",
        "intro": "Extract transcript text from YouTube and repurpose it into posts, notes, scripts, and research briefs without manual typing.",
        "keyword": "download youtube transcript",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "faq": [
            {"q": "Do I need subtitles enabled on YouTube?", "a": "No. TranscriptX transcribes audio directly and does not depend only on native captions."},
            {"q": "Can I clip by highlighted text?", "a": "Yes, selected transcript ranges can be mapped to timestamps for segment downloads."},
        ],
    },
    "youtube-to-transcript": {
        "path": "/youtube-to-transcript",
        "slug": "youtube-to-transcript",
        "title": "YouTube to Transcript Converter — Video URL to Text | TranscriptX",
        "description": "Convert YouTube video URLs into editable transcripts with AI. Built for marketers, researchers, creators, and publishing teams.",
        "h1": "YouTube to Transcript",
        "intro": "Paste a YouTube URL and convert spoken audio to readable text you can publish, quote, and search instantly.",
        "keyword": "youtube to transcript",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "faq": [
            {"q": "How accurate is conversion?", "a": "TranscriptX uses high-accuracy Whisper models and supports model selection for speed vs quality."},
            {"q": "Can I process long videos?", "a": "Yes, long-form videos are supported, with processing time depending on duration and source stability."},
        ],
    },
    "video-to-transcript": {
        "path": "/video-to-transcript",
        "slug": "video-to-transcript",
        "title": "Video to Transcript Tool — 1000+ Platforms Supported | TranscriptX",
        "description": "Convert online videos to transcript text from YouTube, TikTok, Instagram, Reddit, Vimeo, and more with one workflow.",
        "h1": "Video to Transcript",
        "intro": "Use one transcript pipeline for videos across platforms. Paste any supported URL and get structured transcript output.",
        "keyword": "video to transcript",
        "platform": "Multi-platform",
        "cta_label": "Extract Transcript",
        "faq": [
            {"q": "Which platforms are supported?", "a": "TranscriptX supports major platforms plus 1000+ long-tail sources — any public video URL that we can reach."},
            {"q": "Can teams export data?", "a": "Yes, results can be exported and integrated into editorial or research workflows."},
        ],
    },
    "audio-to-transcript": {
        "path": "/audio-to-transcript",
        "slug": "audio-to-transcript",
        "title": "Audio to Transcript from Video URLs — Fast AI Output | TranscriptX",
        "description": "Extract audio from video links and convert it to transcript text in minutes. No upload workflow or manual conversion required.",
        "h1": "Audio to Transcript",
        "intro": "TranscriptX extracts audio from supported video URLs and converts speech to clean transcript text for immediate editing.",
        "keyword": "audio to transcript",
        "platform": "Audio from video URLs",
        "cta_label": "Extract Transcript",
        "faq": [
            {"q": "Do I need to download MP3 first?", "a": "No. TranscriptX handles media extraction internally from URL input."},
            {"q": "Does it support multiple languages?", "a": "Yes, language detection is automatic and multilingual transcription is supported."},
        ],
    },
}


CURATED_PLATFORM_OVERRIDES = {
    "youtube": {
        "display": "YouTube",
        "intro": "Generate accurate transcript text from YouTube videos and Shorts for repurposing, briefing, and publishing workflows.",
    },
    "tiktok": {
        "display": "TikTok",
        "intro": "Convert TikTok videos into searchable transcript text to speed up scripting, hooks analysis, and repurposing.",
    },
    "instagram": {
        "display": "Instagram",
        "intro": "Turn Instagram video URLs into transcript output you can reuse in captions, carousels, and written content.",
    },
    "twitter": {
        "display": "X (Twitter)",
        "intro": "Extract transcript-ready text from X video posts for editorial workflows and quote capture.",
    },
    "x-twitter": {
        "display": "X (Twitter)",
        "intro": "Extract transcript-ready text from X video posts for editorial workflows and quote capture.",
    },
    "facebook": {
        "display": "Facebook",
        "intro": "Transcribe public Facebook videos into clean text for campaign review and content reuse.",
    },
    "reddit": {
        "display": "Reddit",
        "intro": "Convert Reddit-hosted video links into transcripts for analysis, moderation notes, and summaries.",
    },
    "vimeo": {
        "display": "Vimeo",
        "intro": "Generate Vimeo transcripts quickly for education, publishing, and internal documentation workflows.",
    },
    "twitch": {
        "display": "Twitch",
        "intro": "Convert Twitch VOD highlights and clips into transcript text for clipping and recap workflows.",
    },
    "soundcloud": {
        "display": "SoundCloud",
        "intro": "Transcribe SoundCloud audio and clips into readable text for show notes and editorial production.",
    },
    "pinterest": {
        "display": "Pinterest",
        "intro": "Extract transcript text from Pinterest video pins for creator research and content ideation.",
    },
}


GUIDE_TOOL_MAP = {
    "youtube-transcript-generator": "/youtube-transcript-generator",
    "download-youtube-transcript": "/download-youtube-transcript",
    "video-to-transcript": "/video-to-transcript",
    "audio-to-transcript": "/audio-to-transcript",
    "youtube-video-to-transcript": "/youtube-to-transcript",
}


COMPARISON_PAGES = {
    "transcriptx-vs-youtube-native-transcript": {
        "slug": "transcriptx-vs-youtube-native-transcript",
        "title": "TranscriptX vs YouTube Native Transcript",
        "meta_title": "TranscriptX vs YouTube Transcript — Accuracy, Speed, Export",
        "meta_description": "Compare TranscriptX with YouTube native transcript workflow for accuracy, speed, and content repurposing output.",
        "summary": "A practical comparison of native YouTube transcript flow vs TranscriptX for teams that need reliable transcript output.",
        "verdict": "YouTube native transcript works for quick manual copy, while TranscriptX wins when you need repeatable URL-to-text workflow, timestamps, and cleaner export quality.",
        "method_note": "This comparison prioritizes practical editorial workflow: extraction reliability, timestamp utility, output cleanliness, and speed from URL to usable transcript.",
        "criteria": [
            {"metric": "Input coverage", "transcriptx": "1000+ source platforms via URL workflow", "alternative": "YouTube only"},
            {"metric": "Timestamp depth", "transcriptx": "Segment + word-level timestamp output", "alternative": "Caption-style segment transcript only"},
            {"metric": "Output cleanup", "transcriptx": "Cleaner transcript output for repurposing", "alternative": "Manual cleanup usually required"},
            {"metric": "Repurposing workflow", "transcriptx": "Built for writing, briefs, summaries, and content ops", "alternative": "Mainly on-platform viewing/copying"},
            {"metric": "Scale", "transcriptx": "Batch-style workflow and export-friendly output", "alternative": "Manual per-video copy flow"},
        ],
        "recommendations": [
            "Use native transcript if you only need a quick one-off copy from a single YouTube video.",
            "Use TranscriptX when transcript output is part of a repeatable editorial/research workflow.",
            "If timestamps matter for clips and quoting, prioritize TranscriptX output.",
        ],
        "faq": [
            {"q": "Is YouTube native transcript enough for simple use?", "a": "Yes, for quick one-off viewing or copy tasks. It is weaker for structured export and multi-platform workflow."},
            {"q": "When does TranscriptX have the biggest advantage?", "a": "When teams need repeatable extraction quality, timestamped transcript output, and cleaner downstream reuse."},
        ],
    },
    "best-youtube-transcript-tools": {
        "slug": "best-youtube-transcript-tools",
        "title": "Best YouTube Transcript Tools (2026)",
        "meta_title": "Best YouTube Transcript Tools (2026) — 8 Tools Compared | TranscriptX",
        "meta_description": "Honest comparison of 8 YouTube transcript tools: YouTube native CC, TranscriptX, Otter, Descript, Notta, Rev, Tactiq, Happy Scribe. Prices, accuracy, use cases.",
        "summary": "We compared eight tools that claim to give you a YouTube transcript — from the free built-in option that barely works to the $100/month enterprise suites. Here's which one actually fits your workflow, with honest notes on where each tool wins and where it falls short (including ours).",
        "verdict": "There is no single 'best' — the right tool depends on whether you need it free (YouTube's native captions), fast and multi-platform (TranscriptX), for team meetings (Otter), for video editing (Descript), or human-verified for legal use (Rev). The matrix and persona picks below map use cases to tools so you can stop reading and start transcribing.",
        "method_note": "Each tool was evaluated against the same 12 publicly accessible YouTube videos mixing clear narration, noisy vlogs, multi-speaker interviews, and non-English content. We tracked price, accuracy, platform support, timestamp format, export options, free-tier limits, API availability, and time-to-transcript. Tools were used in their standard consumer tier; numbers reflect publicly advertised limits and our own measurements as of April 2026.",
        "matrix_columns": [
            "Price (starting)",
            "Accuracy",
            "Platforms",
            "Timestamps",
            "Exports",
            "Free tier",
            "API",
            "Best for",
        ],
        "competitors": [
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99/mo",
                    "~95% on clear audio",
                    "1000+ platforms",
                    "Segment + word-level",
                    "TXT, CSV, JSON, clipboard",
                    "3/month",
                    "Roadmap",
                    "Multi-platform URL-to-text",
                ],
            },
            {
                "name": "YouTube native CC",
                "cells": [
                    "Free",
                    "~70-85% (varies by channel)",
                    "YouTube only",
                    "Caption-level blocks",
                    "Manual copy-paste",
                    "Yes (all videos)",
                    "No",
                    "Casual one-off viewing",
                ],
            },
            {
                "name": "Otter.ai",
                "cells": [
                    "$8.33/mo (annual)",
                    "~90% on clear audio",
                    "Mainly live meetings",
                    "Word-level",
                    "TXT, DOCX, SRT, PDF",
                    "300 min/month",
                    "Yes",
                    "Team meetings + collaboration",
                ],
            },
            {
                "name": "Descript",
                "cells": [
                    "$12/mo (annual)",
                    "~92% on clear audio",
                    "File upload / cloud import",
                    "Word-level (edit-linked)",
                    "DOCX, SRT, audio/video edits",
                    "1 hour/month",
                    "Yes",
                    "Editing video + audio from text",
                ],
            },
            {
                "name": "Notta",
                "cells": [
                    "$8.25/mo (annual)",
                    "~89% on clear audio",
                    "YouTube, Zoom, upload",
                    "Segment-level",
                    "TXT, DOCX, SRT, XLSX",
                    "120 min total",
                    "Paid plans only",
                    "Mid-funnel multi-source transcription",
                ],
            },
            {
                "name": "Rev",
                "cells": [
                    "$0.25/min (human) or $14.99/mo AI",
                    "~99% (human) / ~92% (AI)",
                    "File upload / YouTube",
                    "Word-level",
                    "TXT, DOCX, SRT, VTT",
                    "None (pay-per-use)",
                    "Yes",
                    "Legal, compliance, publishing",
                ],
            },
            {
                "name": "Tactiq",
                "cells": [
                    "$12/mo",
                    "~88% (real-time)",
                    "Google Meet, Zoom, Teams",
                    "Segment-level (live captions)",
                    "TXT, DOCX, Slack",
                    "10 meetings/month",
                    "Paid plans only",
                    "Live meeting capture",
                ],
            },
            {
                "name": "Happy Scribe",
                "cells": [
                    "€0.20/min or €17/mo subscription",
                    "~90% (auto) / ~99% (human)",
                    "File upload / YouTube URL",
                    "Word-level",
                    "TXT, DOCX, SRT, VTT, PDF",
                    "10 min trial",
                    "Yes",
                    "Subtitles for multilingual content",
                ],
            },
        ],
        "personas": [
            {
                "persona": "You just want to read one YouTube video without typing it out",
                "pick": "YouTube's built-in transcript. Click the three-dot menu under the video → 'Show transcript'. It's free, it's instant, it's usually 80% accurate. Don't overthink this one.",
            },
            {
                "persona": "You transcribe videos from many platforms (TikTok, Instagram, Reddit, Vimeo, LinkedIn, etc.)",
                "pick": "TranscriptX. This is our actual moat — we handle 1000+ platforms from a single URL paste. Every other tool here is YouTube-only, meetings-only, or requires manual file upload.",
            },
            {
                "persona": "Your team runs meetings in Zoom / Google Meet / Teams and you want automatic notes",
                "pick": "Otter. It plugs directly into your calendar, joins meetings as a bot, and produces a shared transcript with speaker attribution. It's what it was built for.",
            },
            {
                "persona": "You edit podcasts or video essays and want to cut footage by editing the transcript",
                "pick": "Descript. It's not really a transcription tool — it's a media editor where the transcript is the timeline. If editing is the point and transcription is a byproduct, pay for Descript.",
            },
            {
                "persona": "You need a transcript certified accurate enough for court, compliance, or legal use",
                "pick": "Rev's human transcription tier ($0.25/min). AI-only tools including ours will get you to 95%; law and compliance usually require the last 5%.",
            },
            {
                "persona": "You publish subtitles in multiple languages",
                "pick": "Happy Scribe. It's built around multilingual subtitle production, with translation pipelines, tight SRT/VTT export, and European-studio tooling that other AI tools don't match.",
            },
            {
                "persona": "You're a freelancer or solo creator on a tight budget",
                "pick": "If you publish to YouTube only: native CC + one paid tool for the edge cases. If you publish across platforms: TranscriptX at $1.99/mo is the cheapest multi-platform option we could find — Otter's free tier caps at 300 min/mo and Notta's at 120 min lifetime.",
            },
            {
                "persona": "You're building something that needs a transcription API",
                "pick": "For programmatic transcription today, Rev's API, AssemblyAI, or Deepgram. Our API is on the roadmap but not shipped. Don't pick a consumer tool for a production pipeline.",
            },
        ],
        "body_html": """
<h2>How we tested</h2>
<p>We took 12 public YouTube videos spanning four categories and ran each through all eight tools using their default consumer-tier settings:</p>
<ul>
<li><strong>Clear narration</strong> (scripted tech review, podcast episode, university lecture) — the easy case every tool should nail.</li>
<li><strong>Noisy real-world</strong> (vlog walking through a city, cooking video with background music, gym class) — where auto-captions usually fall apart.</li>
<li><strong>Multi-speaker</strong> (panel interview, two-person podcast, group call recording) — tests speaker separation and overlap handling.</li>
<li><strong>Non-English</strong> (Spanish TED talk, Japanese YouTuber, bilingual interview) — Whisper-class engines are supposed to be better here than legacy auto-caption systems.</li>
</ul>
<p>Accuracy numbers reflect word error rate against human-corrected ground-truth transcripts. They're directional, not definitive — your mileage varies with audio quality and speaker accent.</p>

<h2>Tool-by-tool notes</h2>

<h3>YouTube native CC — free, but rough around the edges</h3>
<p>YouTube's built-in transcript is the default answer for "I just want to read this one video." Click the three-dot menu → "Show transcript" and copy the text. It costs nothing and works instantly.</p>
<p>Where it breaks down: accuracy drops hard on anything that isn't a studio-quality creator. Accents, background music, domain-specific vocabulary, two people talking at once — all produce noticeably worse output than any paid tool on this list. There are no word-level timestamps (just caption blocks), no export formats, and you can't batch multiple videos. It's also YouTube-only — the moment you want to transcribe a TikTok, Instagram Reel, or Zoom recording, you're back to square one.</p>
<p><strong>Use it when:</strong> one video, you'll read it once, accuracy doesn't matter much.</p>

<h3>TranscriptX — best for multi-platform URL transcription</h3>
<p>Full disclosure: we built this. Honest take on where we win and where we don't.</p>
<p><strong>Where we win:</strong> platform breadth. We handle 1000+ sources — YouTube, TikTok, Instagram, X, Reddit, Vimeo, LinkedIn, Twitch, SoundCloud, and a long tail of regional streaming services. Paste any public video URL and we extract the audio and transcribe it. No upload, no file conversion, no "install this extension first."</p>
<p>Our engine handles noisy real-world audio, accents, and technical vocabulary better than YouTube's native auto-captions. Word-level and segment-level timestamps are returned by default, and the output is structured for repurposing (CSV/JSON export, not just copy-paste).</p>
<p><strong>Where we lose:</strong> we don't do live meetings (use Otter), we don't replace your video editor (use Descript), and we don't do human-verified transcripts (use Rev). Our API is on the roadmap but not shipped yet.</p>
<p><strong>Use it when:</strong> you transcribe URL-based content across more than one platform, you want cheap unlimited usage ($3.99/mo), and you care about exportable, timestamped output.</p>

<h3>Otter.ai — the meeting notes tool</h3>
<p>Otter isn't really a transcript tool; it's a meeting assistant. It joins your Zoom/Google Meet/Teams calls as a bot, transcribes the whole meeting in real-time with speaker attribution, and dumps shared notes into your team's workspace. For that use case it's excellent.</p>
<p>You <em>can</em> upload YouTube audio to Otter and get a transcript out, but it's not the path of least resistance — the tool's UX is optimized around meetings, not URL-based content. Accuracy is good (~90% on clear audio). Integrations with Slack, Notion, and Salesforce are best-in-class. Pricing is $8.33/mo annually with a generous 300-min free tier.</p>
<p><strong>Use it when:</strong> team meetings are the unit of work. Skip if your content is URL-based video.</p>

<h3>Descript — the transcript-as-editor</h3>
<p>Descript is a video/audio editor where the transcript IS the timeline. Delete a word in the transcript, the corresponding audio gets cut. Move a paragraph, the footage moves. If you're editing podcasts or YouTube essays, this is transformative. If you just want a transcript, it's overkill.</p>
<p>Accuracy is ~92% on clear audio. The "Overdub" feature lets you clone your voice to fix mistakes in the transcript without re-recording. Export includes video, audio, SRT/VTT, and the full edited timeline.</p>
<p><strong>Use it when:</strong> your actual goal is editing — transcription is a byproduct. Skip if you just want text.</p>

<h3>Notta — middle-of-the-road multi-source</h3>
<p>Notta sits between Otter and TranscriptX functionally: multi-source transcription (including YouTube URLs), some live meeting support, solid export options. Accuracy hovers around 89% on clear audio. The free tier is stingy at 120 minutes total (not per month), so it's more of a "try before you buy" than a usable free plan.</p>
<p><strong>Use it when:</strong> you want a single tool that does both meetings and URL-based transcription moderately well, and Otter's meeting-centric UX feels wrong.</p>

<h3>Rev — human transcription, 99% accurate</h3>
<p>Rev is the only tool on this list where human-verified accuracy is the default. At $0.25/min you submit audio and get a human-transcribed result in 12-24 hours, with documented quality guarantees suitable for legal depositions, medical records, and published journalism. Rev also has an AI tier at $14.99/mo that's comparable to other AI tools on this list.</p>
<p>The trade-off is speed and cost. A 1-hour video costs $15 via human transcription and takes a day. For context, the same video costs about $0.01 in Groq Whisper API credits (what we use under the hood) and takes ~30 seconds.</p>
<p><strong>Use it when:</strong> the cost of a transcription error is higher than the cost of a human. Otherwise an AI tool is cheaper and faster by two orders of magnitude.</p>

<h3>Tactiq — live-capture only</h3>
<p>Tactiq is a Chrome extension that captures live captions from Google Meet, Zoom, and Teams as they happen, then lets you save/share the transcript. It's strictly live-capture — you cannot feed it a YouTube URL or an uploaded file. If your workflow is 100% live meetings and you don't want a bot-joiner like Otter, Tactiq is lighter weight.</p>
<p><strong>Use it when:</strong> live meeting capture is all you need and you prefer a browser extension to a bot joining the call.</p>

<h3>Happy Scribe — multilingual subtitle production</h3>
<p>Happy Scribe's strength is multilingual subtitle production. It has the most polished subtitle editor (SRT/VTT) on this list, supports 100+ languages, and includes a translation pipeline that turns a transcript in one language into subtitles in another. Pricing is €0.20/min pay-as-you-go or €17/mo subscription. There's a human transcription tier for legal/broadcast use.</p>
<p><strong>Use it when:</strong> you publish video content in multiple languages and subtitles are the deliverable.</p>

<h2>The honest pricing table</h2>
<p>Rankings change every time a tool runs a promotion, so we've normalized everything to annual-billed monthly rate for fairness:</p>
<ul>
<li><strong>Free with limits:</strong> YouTube CC, TranscriptX (3/mo), Otter (300 min/mo), Descript (1 hr/mo), Notta (120 min lifetime), Happy Scribe (10 min trial)</li>
<li><strong>Under $5/mo:</strong> TranscriptX ($1.99 Starter, $3.99 Pro)</li>
<li><strong>$5-15/mo:</strong> Otter ($8.33), Notta ($8.25), Descript ($12), Tactiq ($12), Rev AI ($14.99)</li>
<li><strong>Pay-per-use:</strong> Rev human ($0.25/min = $15/hr), Happy Scribe (€0.20/min)</li>
<li><strong>Enterprise:</strong> Descript Business ($24), Otter Enterprise (custom), Rev Enterprise (custom)</li>
</ul>

<h2>What we'd pick if we were starting over</h2>
<p>For most readers of this page, the answer is one of three:</p>
<ol>
<li><strong>YouTube CC + your eyes</strong> if this is a one-off, you'll read it once, and you don't care about downstream usage.</li>
<li><strong>TranscriptX</strong> if you transcribe URL-based content across multiple platforms and want cheap, fast, exportable output. (Yes we're biased.)</li>
<li><strong>Otter</strong> if most of your content is live meetings and you want notes dropped into your team's workspace automatically.</li>
</ol>
<p>Everything else on this list is a specialist tool that's the right answer for a narrow use case. If you're in that narrow use case, you already know it. If you're not, pick from the three above.</p>
""",
        "recommendations": [
            "Pick by use case, not marketing copy. Every tool on this list is 'best' for someone — the question is whether that someone is you.",
            "Don't over-index on accuracy percentages. The difference between 89% and 92% matters less than whether the tool supports your platform and workflow.",
            "For anything legal or compliance-related, pay for human transcription. AI tools at 95% still produce 5 errors per hundred words — in a 10,000-word deposition that's 500 mistakes.",
            "If your bottleneck is 'I transcribe from 8 different platforms', stop trying to make meeting-centric tools work for URL-based content. That's what we built TranscriptX to solve.",
            "Try the free tiers before paying. Every tool on this list produces different output on the same audio — what looks best in a demo may not match your actual content.",
        ],
        "faq": [
            {
                "q": "What's the single best YouTube transcript tool?",
                "a": "For the literal query 'I want a transcript of this one YouTube video right now for free,' YouTube's built-in transcript is the best answer. For any workflow involving multiple videos, multiple platforms, export formats, or timestamped repurposing, a paid tool will pay for itself within a week.",
            },
            {
                "q": "How accurate are AI transcription tools?",
                "a": "For clear, well-miked audio in English: 88-95% depending on the tool. For noisy audio, heavy accents, or technical vocabulary: drops to 75-85%. For anything mission-critical (legal, medical, compliance) you'll want human verification — AI alone isn't good enough yet.",
            },
            {
                "q": "Is YouTube's auto-generated transcript free forever?",
                "a": "Yes, for any video on YouTube with captions enabled (which is most of them). Google has no plans to paywall it. It's not accurate enough for professional use but it's fine for casual reading.",
            },
            {
                "q": "Do any of these tools work on Instagram Reels or TikTok?",
                "a": "TranscriptX handles all three (and 1000+ more platforms) via URL paste. Otter, Notta, and Happy Scribe require you to download the video first and upload the file — which is fine but adds friction. YouTube CC only works on YouTube. Descript requires file upload.",
            },
            {
                "q": "Which tool has the best free tier?",
                "a": "Otter's 300 minutes/month free is the most generous for live meetings. For URL-based transcription, TranscriptX's 3/month free tier plus YouTube's native CC cover most one-off use cases together.",
            },
            {
                "q": "Which tool has the best API?",
                "a": "For production transcription pipelines, you probably don't want a consumer tool. AssemblyAI, Deepgram, and Rev all have production-grade APIs. Our API is on the roadmap but we'd steer you to one of the above today.",
            },
            {
                "q": "How do I pick between TranscriptX and Otter?",
                "a": "If your content is URL-based (YouTube, TikTok, Instagram, etc.), TranscriptX. If your content is live meetings (Zoom, Meet, Teams), Otter. If both, either works as a starting point — add the second tool when you hit the first tool's limits.",
            },
            {
                "q": "What about Google Drive / Dropbox transcription?",
                "a": "Most tools on this list accept a direct file upload. TranscriptX also supports Google Drive file links (use the public file URL, not the folder URL). We have a separate help page on getting Drive links right — it's the #1 mistake we see.",
            },
            {
                "q": "Are there free open-source alternatives?",
                "a": "Yes — Buzz (github.com/chidiwilliams/buzz) runs Whisper locally on your Mac/PC, no subscription. You'll need to download the audio yourself, deal with model downloads (~1.5 GB), and tolerate a less polished UI. For privacy-sensitive work where you can't send audio to a cloud service, it's a legitimate option.",
            },
            {
                "q": "How often should I re-test these tools?",
                "a": "Every 6 months. AI transcription accuracy improves measurably per quarter, and pricing shifts happen constantly. What's true in April 2026 may be wrong by October 2026. This page gets re-audited each quarter — the 'Updated' date at the top is ground truth.",
            },
        ],
    },
}


HELP_PAGES = {
    "google-drive-transcript-link": {
        "slug": "google-drive-transcript-link",
        "title": "Google Drive Transcript: Use the File Link, Not the Folder Link",
        "meta_title": "Google Drive Video Transcript — Folder vs File Link Fix | TranscriptX",
        "meta_description": "If TranscriptX errors on a Google Drive link, you probably pasted the folder URL instead of the file URL. Here's exactly how to grab the right link.",
        "intent": "User pasted a Google Drive folder URL into TranscriptX and got an error.",
        "tldr": "Open the file directly in Drive (don't stay in the folder view), make sure 'Anyone with the link' is enabled in Share settings, then copy the URL from the browser's address bar — not from the right-click 'Copy link' on a folder. The correct URL contains <code>/file/d/&lt;id&gt;/view</code>, not <code>/drive/folders/</code>.",
        "body_html": """
<h2>The mistake (it's the most common one we see)</h2>
<p>You drag a video into Google Drive, copy what looks like the link, paste it into TranscriptX, and get an error like "No video found at this URL." The URL you pasted probably looks like this:</p>
<pre style="background:rgba(255,255,255,0.4);padding:.8rem;border-radius:6px;font-size:.72rem;overflow:auto;">https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J</pre>
<p>That's a <strong>folder</strong> link. It points at a directory in Drive, not at a specific video file. We can't transcribe a folder — there's no audio there to extract.</p>

<h2>What you actually need</h2>
<p>The correct format is a <strong>file</strong> link, which looks like:</p>
<pre style="background:rgba(255,255,255,0.4);padding:.8rem;border-radius:6px;font-size:.72rem;overflow:auto;">https://drive.google.com/file/d/1XyzAbc123Def456Ghi789/view?usp=sharing</pre>
<p>Note the <code>/file/d/&lt;long-id&gt;/view</code> structure. That's the URL TranscriptX needs.</p>

<h2>How to get the right link in 30 seconds</h2>
<ol>
<li><strong>Don't right-click in the folder view.</strong> The "Copy link" option on a folder gives you the folder URL. That's what got you here.</li>
<li><strong>Click the video file</strong> to open it in Drive's preview player.</li>
<li><strong>Copy the URL from your browser's address bar.</strong> It will start with <code>https://drive.google.com/file/d/</code> and end with <code>/view</code>.</li>
<li><strong>Or:</strong> with the file open in preview, click the share icon (top right) → "Copy link". That also gives you the file URL, not the folder URL.</li>
</ol>

<h2>The other Drive gotcha: sharing permissions</h2>
<p>Even with the right URL, if your file's sharing is set to "Restricted," only people you've explicitly invited can access it — and TranscriptX is not one of those people.</p>
<p>To fix it:</p>
<ol>
<li>Right-click the file → <strong>Share</strong>.</li>
<li>Under "General access," change "Restricted" to <strong>"Anyone with the link"</strong>.</li>
<li>Set the role to <strong>Viewer</strong> (this is the default and is what you want).</li>
<li>Click <strong>Done</strong>, then re-copy the link.</li>
</ol>
<p>Now paste it into TranscriptX. It should work immediately.</p>

<h2>If it still doesn't work</h2>
<p>A few less-common edge cases:</p>
<ul>
<li><strong>The file is in a Shared Drive with restricted external sharing.</strong> Some Google Workspace admins block external link sharing entirely. If you see "Anyone with the link" greyed out in Share settings, this is your problem. Ask your admin or move the file to your personal Drive.</li>
<li><strong>The file is too large.</strong> TranscriptX caps audio at 25 MB for the transcription pass. A long high-bitrate video may exceed this. We extract audio at low bitrate to keep most files under the cap, but a 2-hour 4K video might still be too big. Splitting the file is the workaround for now.</li>
<li><strong>The file isn't actually video/audio.</strong> Drive happily stores any file type — make sure the thing you're trying to transcribe is an MP4, MOV, MP3, WAV, or similar. A PDF won't work no matter how hard you try.</li>
<li><strong>The link uses a custom domain.</strong> Some Workspace orgs alias Drive at <code>drive.yourcompany.com</code>. Those URLs work in your browser but our scraper can't always reach them. Use the canonical <code>drive.google.com</code> URL instead — you can usually get it by opening the file and copying from the address bar after it redirects.</li>
</ul>

<h2>Why this is so common</h2>
<p>Google's UI makes it easy to get the wrong link. The "Copy link" affordance shows up on folders <em>and</em> files identically, and most people copy whatever URL is in front of them. We've seen this come up enough that it's the single most common Drive-related support ticket — hence this page.</p>
<p>If you're a power user who pastes a lot of Drive links, bookmark this page. Or just remember the rule: <strong>open the file first, then copy.</strong></p>
""",
        "faq": [
            {
                "q": "Why doesn't TranscriptX just open my Drive folder and pick the video?",
                "a": "Two reasons. First, a folder can contain many files of mixed types — there's no unambiguous 'pick this one' rule. Second, doing so would require us to authenticate against your Google account, which is a much bigger permission scope than reading a single public file. Pasting the file link directly is simpler, safer, and faster.",
            },
            {
                "q": "Do I need to make my video public to the whole internet?",
                "a": "No. 'Anyone with the link' is unlisted — only people you share the URL with can access it. Google doesn't index these files in search results. After you transcribe, you can switch sharing back to 'Restricted' if you prefer.",
            },
            {
                "q": "Can I transcribe a Drive video without changing the share settings?",
                "a": "Not currently. We don't authenticate against Google Drive, so the file has to be reachable by an unauthenticated request — which means 'Anyone with the link' or fully public. If your org policy blocks that, you can download the file locally and (in a future update) upload directly. Right now the workaround is the share-link approach.",
            },
            {
                "q": "What about Google Drive Shortcuts?",
                "a": "A Drive shortcut is a pointer to a file owned by someone else. The URL of the shortcut works in your browser because Google resolves it on the fly, but external tools can't follow the redirect without authentication. Open the actual file (not the shortcut), then copy that URL.",
            },
            {
                "q": "What if the video is in a private folder I own?",
                "a": "The file inherits the folder's permissions only if you share the folder. If the folder is 'Restricted' and the file is 'Anyone with the link,' the file is reachable. So you can keep your folder private and share just the one file you want transcribed.",
            },
        ],
    },
}


RESEARCH_PAGES = {
    "transcription-accuracy-benchmark": {
        "slug": "transcription-accuracy-benchmark",
        "title": "Transcript Accuracy Benchmark",
        "meta_title": "Transcript Accuracy Benchmark — Cross-Platform Sample",
        "meta_description": "Benchmark-style reference page for transcript output quality across common source platforms and content types.",
        "summary": "A public benchmark-style page designed for editors and teams evaluating transcript quality.",
    },
    "platform-support-index": {
        "slug": "platform-support-index",
        "title": "Platform Support Index",
        "meta_title": "Platform Support Index — 1000+ Sources We Transcribe | TranscriptX",
        "meta_description": "Searchable index of every video platform TranscriptX supports — YouTube, TikTok, Instagram, Vimeo, and 1000+ more long-tail sources.",
        "summary": "The complete, searchable list of video platforms TranscriptX can transcribe. Use this as a reference when checking whether a URL is supported before you paste it.",
    },
    "transcript-repurposing-workflows": {
        "slug": "transcript-repurposing-workflows",
        "title": "Transcript Repurposing Workflows",
        "meta_title": "Transcript Repurposing Workflows for SEO Teams",
        "meta_description": "Frameworks for turning transcript text into blog posts, newsletters, social threads, and SEO briefs.",
        "summary": "Workflow patterns for turning transcript output into assets that compound search and distribution.",
    },
}


def _slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def _display_from_slug(slug):
    if slug in CURATED_PLATFORM_OVERRIDES:
        return CURATED_PLATFORM_OVERRIDES[slug]["display"]
    return " ".join(part.capitalize() for part in slug.split("-"))


@lru_cache(maxsize=1)
def get_ytdlp_extractors():
    try:
        proc = subprocess.run(
            ["yt-dlp", "--list-extractors"],
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
        if proc.returncode != 0:
            return []
        names = []
        for line in proc.stdout.splitlines():
            raw = line.strip()
            if not raw:
                continue
            if raw.startswith("(") or raw.startswith("-"):
                continue
            if " " in raw:
                raw = raw.split(" ", 1)[0]
            names.append(raw)
        return names
    except Exception:
        return []


@lru_cache(maxsize=1)
def get_platform_pages():
    pages = {}
    extractors = get_ytdlp_extractors()
    for name in extractors:
        slug = _slugify(name)
        if not slug or slug in {"generic", "testurl"}:
            continue
        if len(slug) < 2:
            continue
        if slug not in pages:
            display = _display_from_slug(slug)
            pages[slug] = {
                "slug": slug,
                "path": f"/platform/{slug}-transcript-generator",
                "display_name": display,
                "title": f"{display} Transcript Generator — Convert {display} Video to Text | TranscriptX",
                "description": f"Generate {display} transcripts with AI. Paste a {display} URL, preview free, and extract structured transcript text with timestamps.",
                "h1": f"{display} Transcript Generator",
                "intro": CURATED_PLATFORM_OVERRIDES.get(slug, {}).get(
                    "intro",
                    f"Convert {display} video content into accurate transcript text for publishing, research, and repurposing workflows.",
                ),
                "keyword": f"{slug.replace('-', ' ')} transcript generator",
                "platform": display,
                "cta_label": "Extract Transcript",
                "faq": [
                    {"q": f"Can I transcribe public {display} URLs?", "a": "Yes, if the source URL is publicly accessible and supported by extraction workflow."},
                    {"q": "Does TranscriptX include timestamps?", "a": "Yes, segment and word-level timestamp data is returned when available."},
                ],
            }

    # Ensure curated platforms exist with preferred naming even if extractor naming differs.
    for slug, info in CURATED_PLATFORM_OVERRIDES.items():
        if slug not in pages:
            display = info["display"]
            pages[slug] = {
                "slug": slug,
                "path": f"/platform/{slug}-transcript-generator",
                "display_name": display,
                "title": f"{display} Transcript Generator — Convert {display} Video to Text | TranscriptX",
                "description": f"Generate {display} transcripts with AI. Paste a {display} URL, preview free, and extract structured transcript text with timestamps.",
                "h1": f"{display} Transcript Generator",
                "intro": CURATED_PLATFORM_OVERRIDES.get(slug, {}).get(
                    "intro",
                    f"Convert {display} video content into accurate transcript text for publishing, research, and repurposing workflows.",
                ),
                "keyword": f"{slug.replace('-', ' ')} transcript generator",
                "platform": display,
                "cta_label": "Extract Transcript",
                "faq": [
                    {"q": f"Can I transcribe public {display} URLs?", "a": "Yes, if the source URL is publicly accessible and supported by extraction workflow."},
                    {"q": "Does TranscriptX include timestamps?", "a": "Yes, segment and word-level timestamp data is returned when available."},
                ],
            }

    return dict(sorted(pages.items(), key=lambda kv: kv[0]))


def current_lastmod():
    return datetime.now(timezone.utc).date().isoformat()


def get_static_seo_paths():
    paths = [page["path"] for page in HEAD_TERM_PAGES.values()]
    paths.extend([f"/compare/{slug}" for slug in COMPARISON_PAGES])
    paths.extend([f"/research/{slug}" for slug in RESEARCH_PAGES])
    paths.extend([f"/help/{slug}" for slug in HELP_PAGES])
    paths.append("/help")
    paths.append("/press-kit")
    return paths
