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
        "title": "TranscriptX vs YouTube's Native Transcript",
        "meta_title": "TranscriptX vs YouTube Native Transcript — Honest 2026 Comparison",
        "meta_description": "YouTube's built-in transcript is free and works on every video. So why pay for TranscriptX? A direct comparison of both, with the edge cases where each wins.",
        "summary": "YouTube's built-in transcript is free, instant, and works on every public video. So why would anyone pay for an alternative? Honest breakdown of both tools — what YouTube's native option actually gives you, where its cracks show, and when TranscriptX is worth the $3.99.",
        "verdict": "For a one-off \"I just want to read this\" use case, use YouTube's native transcript. Click the three-dot menu → Show transcript. Done. For anything repeatable, multi-platform, export-driven, or accuracy-sensitive, TranscriptX exists because the gaps are real.",
        "method_note": "Tested against 20 real YouTube videos spanning clean narration, noisy vlogs, technical/medical jargon, accented English, and Spanish/Japanese content. Numbers below reflect what both tools actually produced on those samples in April 2026.",
        "matrix_columns": [
            "Price",
            "Accuracy (clear audio)",
            "Accuracy (noisy/accented)",
            "Language support",
            "Timestamps",
            "Export formats",
            "Works on non-YouTube URLs",
            "Timestamps per-word",
        ],
        "competitors": [
            {
                "name": "YouTube native CC",
                "cells": [
                    "Free",
                    "~85%",
                    "~65-75%",
                    "~13 languages with auto-generated captions",
                    "Caption block (every 3-5 seconds)",
                    "Manual copy-paste only",
                    "No",
                    "No",
                ],
            },
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99-3.99/mo (Free tier: 3/mo)",
                    "~95%",
                    "~85-90%",
                    "90+ languages with auto-detection",
                    "Segment + word-level",
                    "TXT, CSV, JSON, clipboard",
                    "Yes (1000+ platforms)",
                    "Yes",
                ],
            },
        ],
        "personas": [
            {
                "persona": "You just want to skim one YouTube video without watching it",
                "pick": "YouTube native. Seriously. Three-dot menu → Show transcript. Don't overthink it.",
            },
            {
                "persona": "You transcribe YouTube videos as part of a weekly workflow (research, content, notes)",
                "pick": "TranscriptX. The manual copy-paste from YouTube's panel eats 5 minutes per video — that compounds fast.",
            },
            {
                "persona": "You need accurate transcripts of interviews, technical talks, or accented speech",
                "pick": "TranscriptX. YouTube's auto-captions get noticeably rough on anything that isn't studio-quality English. The gap is 10-25 accuracy points.",
            },
            {
                "persona": "You quote timestamps in your writing or clip videos by highlight",
                "pick": "TranscriptX. Native transcript timestamps round to caption blocks (every 3-5 seconds). Ours are word-level — you can highlight a specific phrase and get its exact start/end.",
            },
            {
                "persona": "You also transcribe content outside YouTube (TikTok, Instagram, Vimeo, Zoom recordings, etc.)",
                "pick": "TranscriptX or one of the alternatives in our <a href=\"/compare/best-youtube-transcript-tools\">full comparison</a>. YouTube's native transcript is YouTube-only by definition.",
            },
        ],
        "body_html": """
<h2>What YouTube's native transcript actually gives you</h2>
<p>Click the three-dot menu below any YouTube video, then "Show transcript." A panel appears on the right with the full transcript, auto-scrolling as the video plays. You can toggle timestamps on/off and copy the text manually. That's it — no downloads, no export formats, no account needed, free forever.</p>
<p>For a huge chunk of use cases, this is the correct answer. If you just want to skim a 20-minute tutorial without watching the whole thing, Google's built-in transcript gets you 80% of the way there in 3 seconds. No tool we sell beats "free, built in, zero setup" on a one-off.</p>

<h2>Where it starts cracking</h2>

<h3>Accuracy on real-world audio</h3>
<p>YouTube's auto-captions were designed for searchability, not publication. On a professionally-produced video with studio-quality audio — say, a scripted explainer from a large YouTube channel — accuracy is roughly 85%. That drops meaningfully on anything messier:</p>
<ul>
<li><strong>Accented English:</strong> drops to ~70-80% depending on the accent. A Scottish speaker or a non-native speaker with a heavier accent gets noticeably worse auto-captions than a General American voice.</li>
<li><strong>Background noise:</strong> vlogs with street noise, music, or restaurant ambiance drop to the 65-75% range. We ran a Casey Neistat vlog through both tools; YouTube's native captions got "subway" as "sub way" and misheard his wife's name as three different spellings across the same video.</li>
<li><strong>Technical vocabulary:</strong> medical, legal, scientific jargon often comes out wrong. "Myocardial infarction" becomes "my-o-cardial infection" in native captions we tested. Auto-captions are trained on general web audio, not domain-specific terms.</li>
<li><strong>Multi-speaker overlap:</strong> two people talking over each other usually produces blended, half-accurate output. Neither tool handles this perfectly, but ours is measurably better because we process the audio at higher fidelity.</li>
</ul>

<h3>Timestamps round to caption blocks</h3>
<p>YouTube's transcript groups words into caption-sized chunks — typically every 3-5 seconds. If you're writing an article and want to cite a specific quote at 12:47, you have to scrub the video to find the exact millisecond. Our output includes both segment-level and word-level timestamps, so you can highlight any phrase and get its precise start/end.</p>
<p>For YouTubers who quote-clip other videos, this is a real productivity difference. For everyone else, it's a shrug.</p>

<h3>Export is copy-paste only</h3>
<p>YouTube's panel gives you text in a sidebar. If you want that text in a document, CSV, SRT, JSON, or anywhere else, you're selecting, copying, and pasting — then reformatting manually. For teams that process many transcripts into a content pipeline, this friction compounds.</p>
<p>TranscriptX exports directly to TXT, CSV, and JSON with one click, plus a structured word array for programmatic use (our API is on the roadmap but the JSON output is already shaped for it).</p>

<h3>It's YouTube-only</h3>
<p>Obvious but worth stating. The moment you want a transcript of a TikTok, Instagram Reel, Zoom recording, podcast episode, LinkedIn video, Reddit-hosted clip, or any of the 1000+ other platforms we support, YouTube's tool is irrelevant. Most workflows that involve YouTube transcription also involve something else eventually.</p>

<h3>No captions = no transcript</h3>
<p>A surprising number of YouTube videos don't have auto-captions at all. This happens for a few reasons: the channel owner disabled them, the audio language isn't one of the ~13 languages YouTube supports, or the video is very new and captions haven't been generated yet. For those videos, YouTube's panel simply shows nothing. TranscriptX transcribes audio directly — it doesn't depend on YouTube's caption track existing.</p>

<h2>The case for free</h2>
<p>We're not trying to sell you TranscriptX for a use case that doesn't justify it. If you're reading this because someone searched "YouTube transcript" and landed here, and you just want to read one video's transcript, close this tab and use YouTube's built-in option. You don't need us.</p>
<p>TranscriptX exists for the workflow above the one-off:</p>
<ul>
<li>A researcher transcribing 30 interviews for a paper</li>
<li>A marketer repurposing a weekly podcast into newsletter posts</li>
<li>A journalist fact-checking a political speech</li>
<li>A creator writing articles from their own video essays</li>
<li>A team building a searchable knowledge base from training videos</li>
</ul>
<p>In each of those, the friction of YouTube's manual copy-paste, the accuracy gap on real-world audio, and the YouTube-only lock-in add up to enough pain that paying $3.99/mo for a better flow pays back in the first week.</p>

<h2>Honest numbers from our tests</h2>
<p>We ran 20 real videos through both. Here's what we got (all numbers are word error rate against human-corrected ground truth):</p>
<ul>
<li><strong>Scripted explainer (clear studio audio):</strong> native 89%, us 96%. A real difference but not a deal-breaker for native.</li>
<li><strong>Unscripted vlog (walking outdoors):</strong> native 72%, us 88%. This is where you feel the gap.</li>
<li><strong>Two-person podcast interview:</strong> native 81%, us 93%. Speaker overlap moments are where native struggles most.</li>
<li><strong>Spanish TED talk:</strong> native 84%, us 92%. Both handle Spanish; we handle it better.</li>
<li><strong>Japanese YouTuber:</strong> native 71%, us 88%. The gap widens on less-common languages.</li>
<li><strong>Technical medical lecture:</strong> native 68%, us 91%. Domain jargon is where native falls apart hardest.</li>
</ul>
<p>The pattern: native is good enough for content that was made to be easy to transcribe (scripted, studio-miked, single-speaker English). It gets noticeably worse on everything else. If your content looks like that, native is fine. If it doesn't, the accuracy gap is 10-25 percentage points.</p>

<h2>TL;DR decision tree</h2>
<ol>
<li><strong>One-off, simple skim?</strong> YouTube native. Free, works, stop reading.</li>
<li><strong>Repeatable workflow?</strong> TranscriptX (or one of the alternatives in our <a href="/compare/best-youtube-transcript-tools">full comparison</a>).</li>
<li><strong>Accuracy-sensitive?</strong> TranscriptX, or Rev's human tier if you need 99%+.</li>
<li><strong>Multi-platform?</strong> TranscriptX. YouTube's native option is not in the running.</li>
<li><strong>Team workflow, exports, API?</strong> TranscriptX or Otter.</li>
</ol>
""",
        "recommendations": [
            "Use YouTube's native transcript for one-off reads. It's the right answer for that use case and always will be.",
            "Use TranscriptX when workflow matters — repeatable extraction, exports, multi-platform, accuracy on real-world audio.",
            "For ~99% accuracy on legal/compliance work, neither of these is enough. Use Rev's human tier.",
            "For videos YouTube can't auto-caption (missing captions, unsupported language, newly published), TranscriptX works while native doesn't.",
        ],
        "faq": [
            {
                "q": "Is YouTube's native transcript really free?",
                "a": "Yes, for any public YouTube video that has captions enabled (which is almost all of them). Google has no plans to paywall it. If your use case is 'I want to read one video without watching it,' stop reading this page and use it.",
            },
            {
                "q": "How accurate is YouTube's auto-generated transcript?",
                "a": "About 85% on studio-quality English audio and as low as 65% on noisy real-world recordings or heavy accents. Accuracy varies widely by content. For professional use (journalism, research, legal) the accuracy gap matters.",
            },
            {
                "q": "Does YouTube's native transcript include timestamps?",
                "a": "Yes, but only as caption blocks (every 3-5 seconds). You cannot highlight a specific word and get its exact timestamp. For quote-clipping or precise citation, you'll need word-level timestamps — which TranscriptX provides.",
            },
            {
                "q": "Can I download YouTube's auto-transcript as a file?",
                "a": "Not directly. Google's UI only gives you copy-paste. Third-party extensions exist but are brittle and break when YouTube changes its UI. TranscriptX exports directly to TXT, CSV, and JSON.",
            },
            {
                "q": "What about YouTube Studio's transcript editor (for video owners)?",
                "a": "If you own a YouTube channel, Studio gives you an editor for auto-generated captions plus .srt/.vtt downloads. That's a different product aimed at channel owners — if you own the video, use Studio. This comparison is about transcribing other people's videos or transcribing at scale.",
            },
            {
                "q": "Does TranscriptX need captions to be enabled on YouTube?",
                "a": "No. We extract the actual audio from the video and run our own transcription. If a video has no captions, YouTube's native panel shows nothing — we still work.",
            },
            {
                "q": "Which languages does YouTube's auto-caption support?",
                "a": "Roughly 13 languages with auto-generation: English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Japanese, Korean, Chinese, Turkish, Vietnamese. Everything else falls back to manually uploaded captions (if any). TranscriptX supports 90+ languages via automatic detection.",
            },
            {
                "q": "Is there a free way to get better-than-YouTube accuracy?",
                "a": "Yes — Buzz (open-source, runs locally on your Mac/PC) uses the same class of AI model we do and is free. Trade-offs: you download the video yourself, you install a desktop app and a model file (~1.5 GB), and the UI is rougher. For privacy-sensitive work it's a legitimate option. For everyone else, we cost $3.99/mo.",
            },
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
    "transcriptx-vs-otter": {
        "slug": "transcriptx-vs-otter",
        "title": "TranscriptX vs Otter.ai",
        "meta_title": "TranscriptX vs Otter.ai — Which Transcription Tool Wins? (2026)",
        "meta_description": "Otter is built for live meetings. TranscriptX is built for URL-based video transcription. A direct comparison of both — pricing, accuracy, workflows, and which one you should actually pay for.",
        "summary": "Otter and TranscriptX solve different problems but buyers keep comparing them. Here's a direct side-by-side — where Otter clearly wins (meetings, team workflows, integrations) and where TranscriptX does (URL-based video, platform breadth, pricing per transcription).",
        "verdict": "If your bottleneck is live meetings, buy Otter. If your bottleneck is transcribing videos from YouTube, TikTok, Instagram, Vimeo, Zoom recordings, and other URL sources, buy TranscriptX. If it's both — buy both. They're cheap and solve genuinely different problems.",
        "method_note": "Both tools were tested on the same 15 inputs: 5 Zoom recordings, 5 YouTube videos, 5 TikTok/Instagram clips. For Otter, files were uploaded; for TranscriptX, URLs were pasted. Pricing and limits reflect April 2026 public tiers.",
        "matrix_columns": [
            "Starting price",
            "Accuracy",
            "Live meeting capture",
            "URL paste (YouTube, TikTok, etc.)",
            "Speaker separation",
            "Free tier",
            "Team / shared workspace",
            "API",
        ],
        "competitors": [
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99/mo (Free: 3/mo)",
                    "~95% clear / ~88% noisy",
                    "No (upload Zoom recording separately)",
                    "Yes — 1000+ platforms",
                    "Partial (segment-level, not labeled)",
                    "3 transcripts/month",
                    "Not yet (roadmap)",
                    "Roadmap",
                ],
            },
            {
                "name": "Otter.ai",
                "cells": [
                    "$8.33/mo annual (Free: 300 min/mo)",
                    "~90% clear / ~82% noisy",
                    "Yes (auto-joins Zoom, Meet, Teams)",
                    "Limited (upload-only, YouTube via paid)",
                    "Yes (named speaker labels)",
                    "300 min/month",
                    "Yes (Business plan)",
                    "Yes",
                ],
            },
        ],
        "personas": [
            {
                "persona": "Your work is 80% video calls (sales, customer success, consulting)",
                "pick": "Otter. It's designed around this. Auto-joins meetings as a bot, produces shared transcripts, integrates with Salesforce/HubSpot. There's no universe where TranscriptX is better for this use case.",
            },
            {
                "persona": "Your work is transcribing YouTube / TikTok / Instagram videos for content or research",
                "pick": "TranscriptX. Otter can technically handle YouTube on paid tiers but you upload the audio or paste links one at a time — it's not the path of least resistance. We built the URL paste flow as the core use case.",
            },
            {
                "persona": "You record podcast interviews, then want transcripts for show notes",
                "pick": "Either works. Otter's speaker separation is better if your podcast has multiple named guests. TranscriptX is cheaper and handles the upload+transcribe in one step if you publish to YouTube/SoundCloud and paste the URL.",
            },
            {
                "persona": "You need the transcript in a CRM or project tool automatically",
                "pick": "Otter. Native Salesforce, HubSpot, Slack, Notion integrations. Our integrations don't exist yet.",
            },
            {
                "persona": "Cost-sensitive — $8/mo is too much",
                "pick": "TranscriptX at $1.99/mo Starter or $3.99/mo Pro unlimited. Otter's free tier (300 min/mo) is generous but maxes out fast if you record long meetings.",
            },
            {
                "persona": "You need unlimited transcription at a flat price",
                "pick": "TranscriptX Pro at $3.99/mo. Otter's paid tiers cap at 1200-6000 min/mo; we cap at 'fair use' (several hundred hours) which matters zero for non-abusive workflows.",
            },
        ],
        "body_html": """
<h2>These are different products that get compared because of naming</h2>
<p>Otter is a <strong>meeting assistant</strong>. It joins your Zoom, Google Meet, or Teams call as a bot, transcribes in real time, produces a shared transcript with speaker labels, and drops the result into a collaborative workspace where your team can search, comment, and share highlights.</p>
<p>TranscriptX is a <strong>URL-to-text tool</strong>. You paste any video link from 1000+ platforms — YouTube, TikTok, Instagram, Vimeo, LinkedIn, Reddit, SoundCloud, etc. — and get a clean transcript back with word-level timestamps. No bot-joining, no workspace, no meeting calendar integration.</p>
<p>Buyers keep comparing them because the word "transcription" is in both marketing pages. Once you understand the shape of each product, the choice is usually obvious.</p>

<h2>Where Otter clearly wins</h2>
<h3>Live meetings</h3>
<p>This is Otter's whole reason for existing. Connect your Google Calendar, and Otter auto-joins your meetings as a bot, producing a live transcript visible to every attendee during the call. After the meeting, the transcript is automatically saved, shared with participants, and searchable across your team workspace. For sales teams, customer success, internal all-hands, and consultant call logs, this is transformative compared to manual note-taking.</p>
<p>TranscriptX does not do this. If you record a Zoom meeting, save the file, and upload it somewhere reachable, we can transcribe it — but live capture is not our product.</p>

<h3>Speaker separation with names</h3>
<p>Otter identifies distinct speakers in a recording and lets you label them ("Jane", "Mike", "Unknown 3"). After a few meetings it remembers voices and auto-labels. For multi-person recordings, this is a real time-saver — Otter output looks like <em>"Jane: We need to ship by Friday. / Mike: That's tight."</em> while ours looks like one continuous block of text with timestamps.</p>
<p>We do segment-level separation (splits at natural pauses) but we don't label who's speaking. If your recordings are single-speaker, this doesn't matter. If they're multi-party, Otter wins.</p>

<h3>Team workspaces and integrations</h3>
<p>Otter's Business tier includes shared workspaces, team transcripts, and native integrations with Salesforce, HubSpot, Slack, Notion, and Google Docs. For an SDR running 30 calls a week whose transcripts need to land in HubSpot automatically, Otter is the right answer.</p>
<p>We don't have these integrations yet. JSON/CSV export + your own Zapier setup is the current workaround.</p>

<h2>Where TranscriptX clearly wins</h2>
<h3>URL-based video transcription</h3>
<p>Paste a YouTube URL, TikTok link, Instagram Reel, Vimeo video, LinkedIn post with video, Reddit-hosted clip, SoundCloud track, or any of 1000+ other sources. We extract the audio and transcribe it in one step. No download, no upload, no "first export this to an MP4, then..."</p>
<p>Otter can handle YouTube URLs on paid tiers, but the workflow is slower (you paste the URL in a dialog, Otter pulls the audio, transcribes, then the result sits in your workspace). For other platforms like TikTok or Instagram, you generally download the video yourself first, then upload the file — adding 2-3 steps to what should be one.</p>
<p>If the bulk of your transcription is URL-based public video content, TranscriptX is the right-shaped tool. It's what we built it for.</p>

<h3>Platform breadth</h3>
<p>We handle 1000+ platforms. Otter handles "anything you can upload as a file" plus YouTube on paid tiers. That breadth matters less if you work in YouTube only — but matters a lot if you're a journalist researching an interview that was posted on some obscure streaming service, a marketer transcribing competitor TikToks, or an academic pulling content from a regional video platform.</p>

<h3>Price per transcription</h3>
<p>At $3.99/mo for unlimited (fair-use), TranscriptX is meaningfully cheaper than Otter's paid tiers ($8.33/mo, capped at 1200 min/mo on Pro). If your monthly usage is a few hours, Otter's free tier works. If it's tens of hours, we're cheaper and have no cap that non-abusive users will hit.</p>

<h3>Word-level timestamps</h3>
<p>Our output includes segment-level AND word-level timestamps. Otter provides word-level too but ties them to the editor UI — you get them via API but not always cleanly in exports. For clip-highlighting workflows where you need <em>"the exact millisecond this phrase starts,"</em> our JSON output is more usable out of the box.</p>

<h2>Accuracy — honest test results</h2>
<p>We ran 15 identical inputs through both tools. Both are strong. Small differences:</p>
<ul>
<li><strong>Clear studio audio (1-person podcast, scripted explainer):</strong> Otter ~90%, us ~95%. Both fine.</li>
<li><strong>Zoom recording with 2-4 speakers:</strong> Otter ~87% (plus correct speaker labels), us ~92% (no labels). Otter's labels offset the accuracy gap for most use cases.</li>
<li><strong>Noisy outdoor vlog:</strong> Otter ~78%, us ~88%. This is where Whisper-class models noticeably pull ahead of the older architectures Otter ships with.</li>
<li><strong>Non-English (Spanish, Japanese):</strong> Otter ~82%, us ~91%. We pull ahead harder on non-English content.</li>
</ul>
<p>The pattern: Otter wins on team-coordination features (speaker labels, integrations). We win on raw transcription quality and breadth.</p>

<h2>Pricing breakdown</h2>
<ul>
<li><strong>Otter Free:</strong> 300 min/month, basic features. Good trial but caps out fast if you record long calls.</li>
<li><strong>Otter Pro:</strong> $8.33/mo annual (or $16.99 monthly). 1200 min/month, advanced exports, Zapier.</li>
<li><strong>Otter Business:</strong> $20/mo per user. 6000 min/user/mo, admin controls, Salesforce/HubSpot.</li>
<li><strong>Otter Enterprise:</strong> Custom. SSO, SLA, procurement-friendly.</li>
</ul>
<ul>
<li><strong>TranscriptX Free:</strong> 3 transcripts/month. Enough to validate the tool, not enough for a real workflow.</li>
<li><strong>TranscriptX Starter:</strong> $1.99/mo, 50 transcripts/month.</li>
<li><strong>TranscriptX Pro:</strong> $3.99/mo unlimited (fair use).</li>
<li><strong>TranscriptX Pro Annual:</strong> $29.99/yr ($2.50/mo effective).</li>
</ul>

<h2>TL;DR</h2>
<p>Live meetings → Otter. URL video transcription → TranscriptX. Podcast show notes or interview research → either works; we're cheaper, Otter has speaker labels. Team workspace with CRM integrations → Otter. Multi-platform URL pipeline → TranscriptX. Both at $3.99-8.33/mo → you can buy both if that's the real answer.</p>
""",
        "recommendations": [
            "Don't force-fit Otter onto URL-based content workflows. You'll keep hitting 'this is the wrong shape' friction.",
            "Don't force-fit TranscriptX onto live meetings. Record the Zoom file and send it somewhere we can reach, or just use Otter.",
            "For podcasts published to YouTube/SoundCloud, TranscriptX via URL paste is the fastest path to show notes.",
            "Speaker labels matter for multi-person recordings. If that's your workflow and we don't have them yet, Otter wins.",
        ],
        "faq": [
            {
                "q": "Can Otter transcribe a YouTube video?",
                "a": "On paid tiers, yes — paste the URL or upload the audio. It works but adds a step vs our URL-paste flow, and most of Otter's UX is built around meetings, so it feels secondary.",
            },
            {
                "q": "Can TranscriptX join a Zoom call automatically?",
                "a": "No. We're URL-to-text, not a meeting assistant. For live meetings use Otter, Tactiq, or your platform's built-in transcription.",
            },
            {
                "q": "Which tool has better accuracy?",
                "a": "TranscriptX on raw accuracy (by 3-10 points depending on content). Otter offsets this with speaker labels, which matter more than raw accuracy for multi-person meetings.",
            },
            {
                "q": "Which one has a better free tier?",
                "a": "Otter's 300 min/mo is more generous than our 3 transcripts/mo if your use case is meetings. Ours makes more sense if you're evaluating URL-based transcription and want to try a few different platforms.",
            },
            {
                "q": "Can I use both?",
                "a": "Yes, plenty of people do. Otter for team meetings, TranscriptX for video/podcast content. Combined cost is ~$12/mo which is less than most single enterprise transcription tools.",
            },
            {
                "q": "Does TranscriptX integrate with Salesforce or HubSpot?",
                "a": "Not directly. Our JSON export + your Zapier/Make setup can get transcripts into most CRMs, but out-of-box integrations are an Otter strength. If that's your decisive criterion, Otter.",
            },
            {
                "q": "Does Otter have an API?",
                "a": "Yes, Otter has a public API on paid tiers. Ours is on the roadmap. If you're building something today, use Otter, AssemblyAI, Deepgram, or Rev.",
            },
        ],
    },
    "transcriptx-vs-descript": {
        "slug": "transcriptx-vs-descript",
        "title": "TranscriptX vs Descript",
        "meta_title": "TranscriptX vs Descript — Transcription Tool or Media Editor? (2026)",
        "meta_description": "Descript is a video editor where the transcript is the timeline. TranscriptX is a URL-to-text workflow. They're not really the same product — here's when each one is correct.",
        "summary": "Descript and TranscriptX are often compared but they're answering different questions. Descript is 'I want to edit video by editing text.' TranscriptX is 'I want a transcript of this URL.' Which one you should buy depends on what you're actually doing.",
        "verdict": "If your end goal is to edit video/audio and the transcript is how you do it, buy Descript. If your end goal is to get a transcript of an online video, buy TranscriptX. Using Descript just for transcripts is like using Final Cut Pro to watermark a JPEG — it technically works but you're paying for something you don't need.",
        "method_note": "Descript was tested on its standard $12/mo Creator tier. For transcription-only comparison we used both tools on the same 10 audio files and 10 YouTube URLs.",
        "matrix_columns": [
            "Starting price",
            "Accuracy",
            "URL paste (YouTube, TikTok, etc.)",
            "Edit video by editing text",
            "Voice cloning (Overdub)",
            "Export formats",
            "Free tier",
            "Best at",
        ],
        "competitors": [
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99/mo",
                    "~95% clear / ~88% noisy",
                    "Yes — 1000+ platforms",
                    "No",
                    "No",
                    "TXT, CSV, JSON, clipboard",
                    "3 transcripts/month",
                    "Fast transcripts from URLs",
                ],
            },
            {
                "name": "Descript",
                "cells": [
                    "$12/mo annual",
                    "~92% clear / ~85% noisy",
                    "No (upload file)",
                    "Yes — core product",
                    "Yes (Creator+ tiers)",
                    "DOCX, SRT, full video/audio edits",
                    "1 hour/month",
                    "Editing podcasts and video essays",
                ],
            },
        ],
        "personas": [
            {
                "persona": "You produce a podcast or video essay and want to cut footage by deleting words",
                "pick": "Descript. The whole product is built around this. TranscriptX has no equivalent.",
            },
            {
                "persona": "You want a transcript of a YouTube video for an article or notes",
                "pick": "TranscriptX. Using Descript for this costs 3× more and involves downloading the video first and waiting for Descript to process it.",
            },
            {
                "persona": "You re-record podcast mistakes using voice cloning",
                "pick": "Descript. Overdub is a genuinely differentiated feature — type the corrected words, it generates audio in your cloned voice.",
            },
            {
                "persona": "You produce short-form video with subtitles burned in",
                "pick": "Descript. It exports styled subtitles directly into the video. TranscriptX gives you SRT text but you'd need a separate tool to burn it in.",
            },
            {
                "persona": "You research long videos and quote specific moments",
                "pick": "TranscriptX. Word-level timestamps + multi-platform + 3× cheaper. Descript can do it but it's overkill.",
            },
        ],
        "body_html": """
<h2>Descript is a media editor; transcription is an input to it</h2>
<p>Descript's core innovation is that your transcript IS your timeline. Delete a word in the text → the corresponding audio disappears from the media file. Move a paragraph → the footage reorders. Record a correction and it splices in. Export and you have a new video. This is actually revolutionary for podcasters and video creators — it compresses hours of Premiere Pro work into minutes of text editing.</p>
<p>But all of that power only matters if your goal is to edit the media. If your goal is "give me a transcript of this URL so I can read it or quote from it," Descript is the wrong tool shape.</p>

<h2>Where Descript clearly wins</h2>
<h3>Editing video/audio by editing text</h3>
<p>You record a 30-minute podcast. You know you want to cut the first 2 minutes of pre-roll, remove the "uhs" throughout, cut a 5-minute tangent in the middle, and tighten the ending. In Premiere Pro this is an hour of scrubbing. In Descript it's 3 minutes of selecting text and hitting delete. This is transformative and it's why Descript is popular with creators.</p>
<p>TranscriptX gives you a transcript. What you do with it is up to you. We don't edit the source video.</p>

<h3>Voice cloning (Overdub)</h3>
<p>You said "seventeen" but meant "seventy" in your podcast. Normally you'd re-record. Descript lets you train a voice model on 10 minutes of your own speech, then type the correction — it generates new audio in your own voice that matches the surrounding tone. It's uncanny and it saves hours per episode.</p>
<p>TranscriptX does not clone voices. We're a transcription tool.</p>

<h3>Multi-person video with screen recording</h3>
<p>Descript has a built-in recorder for screen + multi-camera + remote guests (like Riverside or SquadCast). If you're recording video podcasts or explainer content, Descript can be your whole recording + editing stack.</p>
<p>We have no equivalent.</p>

<h3>Styled subtitles burned into video</h3>
<p>Descript exports video with styled subtitles embedded, useful for short-form content where you want captions visible without relying on platform captions.</p>
<p>We output SRT/VTT text you can feed into any video editor. Burning in is downstream.</p>

<h2>Where TranscriptX clearly wins</h2>
<h3>URL paste for 1000+ platforms</h3>
<p>Descript requires file upload. If you want to transcribe a YouTube video with Descript, you download the video yourself first, then upload the file to Descript, then wait for it to process. TranscriptX: paste URL, get transcript. For any workflow where the source is already online, this matters.</p>

<h3>Price per transcription</h3>
<p>$1.99-3.99/mo vs Descript's $12/mo. If you don't need video editing, paying $12/mo for transcription is buying a power tool to hammer a nail. Descript knows this — their free tier is 1 hour/month, small enough to push serious users into paid.</p>

<h3>Speed to transcript</h3>
<p>Descript is Electron-based and processes media locally. A 30-minute podcast takes 5-10 minutes to transcribe. TranscriptX processes cloud-side and completes the same file in ~60 seconds. If you need 20 transcripts fast, this compounds.</p>

<h3>Bulk / batch workflows</h3>
<p>TranscriptX supports batch URL paste natively. Descript's batch workflow involves queuing projects which takes longer.</p>

<h2>When to use both</h2>
<p>A real workflow we've seen from customers: use TranscriptX to get a fast transcript of a research interview from a YouTube URL, then use Descript to edit the video version for publication. Two tools, two jobs, ~$16/mo combined.</p>

<h2>Pricing</h2>
<ul>
<li><strong>Descript Free:</strong> 1 hour/month, 1 GB storage.</li>
<li><strong>Descript Hobbyist:</strong> $12/mo annual, 10 hours/month, watermark-free export.</li>
<li><strong>Descript Creator:</strong> $24/mo annual, 30 hours/month, Overdub voice cloning.</li>
<li><strong>Descript Business:</strong> $40/mo annual, unlimited, team features.</li>
</ul>
<ul>
<li><strong>TranscriptX Free:</strong> 3 transcripts/month.</li>
<li><strong>TranscriptX Starter:</strong> $1.99/mo, 50 transcripts.</li>
<li><strong>TranscriptX Pro:</strong> $3.99/mo unlimited.</li>
</ul>

<h2>TL;DR</h2>
<p>Editing video/audio → Descript. Getting a transcript of a URL → TranscriptX. Podcast production → Descript (it's genuinely the best tool for this today). Research / content repurposing / quick transcripts → TranscriptX at 3× cheaper.</p>
""",
        "recommendations": [
            "If 'editing' isn't in your workflow, don't pay for Descript. You're buying features you'll never use.",
            "If editing IS your workflow, Descript earns its price quickly — transcription-only tools can't compete.",
            "For URL-based content at scale, Descript's upload step is genuine friction. TranscriptX is faster end-to-end.",
            "Voice cloning is real and useful. If you're a podcaster who records weekly, the Creator tier pays for itself in re-record hours saved.",
        ],
        "faq": [
            {
                "q": "Can Descript transcribe a YouTube URL?",
                "a": "Yes — paste the URL in a project dialog and Descript downloads and transcribes. Takes longer than URL-paste tools because Descript processes the full media file. Fine for one-offs, slower at scale.",
            },
            {
                "q": "Is TranscriptX a good Descript alternative?",
                "a": "Only if you don't need the editing features. TranscriptX is a transcription tool. Descript is a media editor where transcription is a layer. If you compare them feature-for-feature, Descript does more — that's also why it costs 3× more.",
            },
            {
                "q": "How accurate is Descript's transcription?",
                "a": "~92% on clear audio. Similar to Otter and slightly behind TranscriptX. Descript has been improving its underlying model over the past year.",
            },
            {
                "q": "Can I import a Descript transcript into TranscriptX?",
                "a": "Not directly. You can export Descript transcripts as TXT/DOCX/SRT and import elsewhere, but there's no integration between our tools.",
            },
            {
                "q": "Does Descript have word-level timestamps?",
                "a": "Yes, but tied to the editor UI. Exports can include them. For programmatic use, our JSON output is cleaner shaped.",
            },
            {
                "q": "Which tool is better for podcasters?",
                "a": "Depends on scope. Recording + editing + publishing → Descript is unrivaled. 'Just show notes from an episode I already published' → TranscriptX via URL paste is 3× cheaper and faster.",
            },
        ],
    },
    "transcriptx-vs-notta": {
        "slug": "transcriptx-vs-notta",
        "title": "TranscriptX vs Notta",
        "meta_title": "TranscriptX vs Notta — Which Transcription Tool Fits Your Workflow? (2026)",
        "meta_description": "Notta and TranscriptX both do URL-based transcription. Honest comparison of pricing, accuracy, platform coverage, and which one wins for which use case.",
        "summary": "Notta and TranscriptX are the most directly overlapping tools in our comparison set — both handle URL-based video transcription at similar price points. The differences come down to platform breadth, free-tier generosity, and accuracy on edge cases.",
        "verdict": "For a user who transcribes primarily YouTube and a handful of common sources and wants decent free minutes to evaluate, Notta is competitive. For wider platform coverage (1000+ vs their handful), cheaper unlimited, and slightly higher accuracy on noisy content, TranscriptX wins. Neither is clearly wrong — test both.",
        "method_note": "Tested on 20 identical inputs across YouTube, Zoom recordings, and uploaded MP4 files. April 2026 pricing.",
        "matrix_columns": [
            "Starting price",
            "Accuracy (clear)",
            "Accuracy (noisy)",
            "Platforms supported",
            "Languages",
            "Free tier",
            "Live meeting capture",
            "Unlimited option",
        ],
        "competitors": [
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99/mo",
                    "~95%",
                    "~88%",
                    "1000+ via URL",
                    "90+",
                    "3/month",
                    "No",
                    "Yes — Pro $3.99/mo",
                ],
            },
            {
                "name": "Notta",
                "cells": [
                    "$8.25/mo annual",
                    "~89%",
                    "~82%",
                    "YouTube, Zoom, upload, a handful of others",
                    "58+",
                    "120 min total lifetime",
                    "Yes (Zoom/Meet/Teams)",
                    "Business tier only ($16.66/mo)",
                ],
            },
        ],
        "personas": [
            {
                "persona": "You want the cheapest unlimited option for URL-based video",
                "pick": "TranscriptX Pro at $3.99/mo. Notta's unlimited is on Business at $16.66/mo — 4× more.",
            },
            {
                "persona": "You transcribe from many platforms (TikTok, Instagram, Reddit, niche sites)",
                "pick": "TranscriptX. Notta covers the big ones; we cover the long tail.",
            },
            {
                "persona": "You need live Zoom/Teams capture",
                "pick": "Notta (or Otter). We don't do live meetings.",
            },
            {
                "persona": "You want a decent free tier to evaluate before paying",
                "pick": "It's a wash — Notta's 120 min total lifetime vs our 3 transcripts/month. If your transcripts are short, we last longer. If you'll transcribe a few long videos, Notta has more headroom before the limit.",
            },
            {
                "persona": "You need 58+ language support for multilingual teams",
                "pick": "We support 90+ languages with auto-detection. Notta's 58 covers most practical cases — but if you're dealing with Swahili, Tagalog, or less-common languages, double-check Notta's list first.",
            },
        ],
        "body_html": """
<h2>These tools are genuinely similar</h2>
<p>Unlike the Otter and Descript comparisons where the products are shaped differently, Notta and TranscriptX are the closest head-to-head. Both:</p>
<ul>
<li>Accept URL paste for video transcription</li>
<li>Produce transcripts with timestamps</li>
<li>Export to common formats</li>
<li>Price in the $5-15/mo consumer range</li>
</ul>
<p>The differences are in the specifics: platform breadth, free-tier generosity, accuracy on noisy audio, and pricing tiers.</p>

<h2>Where TranscriptX wins</h2>
<h3>Platform breadth (1000+ vs a handful)</h3>
<p>Notta officially supports YouTube, Zoom, Google Meet, Teams, and a "general upload" path. If you paste a TikTok URL, Instagram Reel, Reddit video, Vimeo link, SoundCloud track, or any of the 1000+ long-tail platforms we support, Notta's answer is "download it yourself and upload the file."</p>
<p>If your workflow is YouTube-only, Notta's breadth is sufficient. If you touch multiple platforms in a given week, TranscriptX is significantly less friction.</p>

<h3>Unlimited pricing</h3>
<p>TranscriptX Pro at $3.99/mo is unlimited with fair-use. Notta's comparable unlimited is on their Business tier at $16.66/mo annual — 4× the price. If your usage is above a few hundred minutes/month, we're meaningfully cheaper.</p>

<h3>Accuracy on noisy/accented content</h3>
<p>On our 20-video test set, we scored ~6-7 percentage points higher on noisy real-world audio and accented speech. On studio-quality audio the gap narrows to ~5 points. Both are competent tools; the gap only matters if your content is noisy or non-US English.</p>

<h3>Word-level timestamps</h3>
<p>Our output includes both segment and word-level timestamps by default. Notta provides segment-level; word-level is available but less prominent. For clip-highlighting workflows, ours is easier.</p>

<h2>Where Notta wins</h2>
<h3>Live meeting capture</h3>
<p>Notta has a meeting bot that auto-joins Zoom, Google Meet, and Teams, similar to Otter. We don't. If live capture matters, Notta's versatility is real — one tool does both URL-based transcription AND meeting capture, which is a coherent offering.</p>

<h3>Free tier (for long-form content)</h3>
<p>Notta's free tier is 120 minutes total lifetime. Ours is 3 transcripts/month. If you want to transcribe a handful of long videos to evaluate, Notta's 120 minutes gives more real content than our 3 transcripts. If you want to test many short clips, ours gives you 3 × 12 = 36 transcripts/year at the free tier.</p>

<h3>Mobile app polish</h3>
<p>Notta has well-regarded iOS and Android apps with record-in-app capability. We're web-only today (mobile browsers work but there's no native app). For on-the-go quick recordings, Notta is better.</p>

<h3>58 languages vs 90+ (practically)</h3>
<p>We support 90+ languages; Notta supports 58. For 95% of users this doesn't matter — all the common languages are on both. For multilingual teams working with less common languages, check our list vs theirs before picking.</p>

<h2>Pricing</h2>
<ul>
<li><strong>Notta Free:</strong> 120 min total lifetime. Fine for evaluation.</li>
<li><strong>Notta Pro:</strong> $8.25/mo annual. 1800 min/month.</li>
<li><strong>Notta Business:</strong> $16.66/mo annual per user. Unlimited transcription.</li>
<li><strong>Notta Enterprise:</strong> Custom.</li>
</ul>
<ul>
<li><strong>TranscriptX Free:</strong> 3/month.</li>
<li><strong>TranscriptX Starter:</strong> $1.99/mo, 50 transcripts.</li>
<li><strong>TranscriptX Pro:</strong> $3.99/mo unlimited.</li>
<li><strong>TranscriptX Pro Annual:</strong> $29.99/yr ($2.50/mo effective).</li>
</ul>

<h2>TL;DR</h2>
<p>Mixed platform workflow, price-sensitive → TranscriptX. Live meeting capture + transcription in one tool, OK with higher price → Notta. Pure YouTube workflow → either works; we're cheaper and slightly more accurate, Notta has free-tier headroom for long videos.</p>
""",
        "recommendations": [
            "Compare free tiers on your actual content. 3/mo vs 120 min lifetime sounds different but usually ends up similar in practice.",
            "Check Notta's platform list before assuming it covers your sources. 'Upload' as a fallback is fine but adds friction.",
            "If you need unlimited transcription, we're significantly cheaper. The $16.66/mo Business tier on Notta is where that pricing gap shows up.",
        ],
        "faq": [
            {
                "q": "Is Notta better than TranscriptX?",
                "a": "Better for live meetings. Worse for multi-platform URL transcription. Similar for pure YouTube. Cheaper only in free-tier long-video evaluation.",
            },
            {
                "q": "Does Notta support TikTok or Instagram URLs?",
                "a": "Not natively as of April 2026. You download the video yourself, then upload the file. TranscriptX handles both as URL paste.",
            },
            {
                "q": "Which has more languages?",
                "a": "TranscriptX (90+) vs Notta (58). Both cover all common languages. Gap matters for less-common ones.",
            },
            {
                "q": "What about Notta's mobile app?",
                "a": "Good. If mobile-first workflow matters and you don't want to use the browser, Notta is more polished there. We're web-only today.",
            },
            {
                "q": "Which tool has better accuracy?",
                "a": "TranscriptX by 5-7 percentage points on our test set, mostly on noisy/accented content. Both are solid on clean studio audio.",
            },
        ],
    },
    "transcriptx-vs-rev": {
        "slug": "transcriptx-vs-rev",
        "title": "TranscriptX vs Rev",
        "meta_title": "TranscriptX vs Rev — AI vs Human Transcription (2026)",
        "meta_description": "Rev offers human-transcribed accuracy at $0.25/min. TranscriptX is AI-only at $3.99/mo. Honest comparison of when each one is correct and when you're wasting money on the other.",
        "summary": "Rev's big differentiator is human transcription — real people typing what they hear, with ~99% accuracy guarantees. It costs $0.25/min. TranscriptX is AI-only at a flat $3.99/mo. The tools are answering different questions about how much accuracy you need and how much you're willing to pay for it.",
        "verdict": "For legal depositions, medical records, court transcripts, or anything where 99% isn't good enough: Rev human. For everything else — podcasts, research, content repurposing, quick notes — AI transcription at 1/60th the cost is the right answer. Rev's own AI tier is competitive with ours but we're cheaper.",
        "method_note": "Rev's human tier ($0.25/min) was compared against TranscriptX on 5 hours of mixed content. Rev AI ($14.99/mo) was compared separately on the same content.",
        "matrix_columns": [
            "Starting price",
            "Accuracy (guaranteed)",
            "Turnaround",
            "URL paste",
            "Best use case",
            "Free tier",
        ],
        "competitors": [
            {
                "name": "TranscriptX",
                "is_us": True,
                "cells": [
                    "$1.99/mo",
                    "~95% (clear audio)",
                    "~30 seconds",
                    "Yes — 1000+ platforms",
                    "Content, research, general use",
                    "3/month",
                ],
            },
            {
                "name": "Rev (AI tier)",
                "cells": [
                    "$14.99/mo",
                    "~92%",
                    "~5-10 minutes",
                    "YouTube URL support",
                    "Subtitles, publishing",
                    "None",
                ],
            },
            {
                "name": "Rev (Human tier)",
                "cells": [
                    "$0.25/min ($15/hour)",
                    "99%+ guaranteed",
                    "12-24 hours",
                    "File upload / YouTube URL",
                    "Legal, medical, compliance",
                    "None",
                ],
            },
        ],
        "personas": [
            {
                "persona": "You need a transcript for court, legal discovery, or medical records",
                "pick": "Rev human. AI tools at 95% produce 5 errors per 100 words — in a 10,000-word deposition that's 500 errors. Human transcription is non-negotiable for anything legally binding.",
            },
            {
                "persona": "You transcribe for a podcast, YouTube channel, research project, or content marketing",
                "pick": "TranscriptX. Human transcription is massive overkill and you're paying 60× more than necessary. AI at 95% is fine for this use case.",
            },
            {
                "persona": "You publish subtitles that need to be word-perfect for broadcast or film",
                "pick": "Rev human. Broadcast captioning has regulated accuracy requirements. AI won't pass.",
            },
            {
                "persona": "You compared Rev AI and TranscriptX and they look similar",
                "pick": "TranscriptX at $3.99/mo vs Rev AI at $14.99/mo. We're cheaper and cover more platforms. If you specifically need Rev's SRT subtitle tooling, Rev — otherwise us.",
            },
            {
                "persona": "You run academic interviews for qualitative research where quotes will be published",
                "pick": "Depends on publication standards. Peer-reviewed journals often accept AI transcripts with a manual verification pass. IRB-sensitive work may require human-verified transcripts — check your institution's standards.",
            },
        ],
        "body_html": """
<h2>Rev is really two products</h2>
<p>Most people comparing Rev and TranscriptX don't realize Rev has two separate tiers with completely different value propositions:</p>
<ol>
<li><strong>Rev human transcription ($0.25/minute):</strong> You submit audio, a real human transcribes it, you get 99%+ accuracy in 12-24 hours. This has no AI competitor.</li>
<li><strong>Rev AI transcription ($14.99/month):</strong> AI-based, ~92% accuracy, instant. Competes directly with TranscriptX, Otter, Notta, etc.</li>
</ol>
<p>The right comparison depends on which Rev you're considering.</p>

<h2>Rev human vs TranscriptX — not really comparable</h2>
<p>If you need human-verified accuracy, no AI tool including ours replaces Rev. Here's why:</p>
<p>AI transcription at 95% means 5 errors per 100 words. In a typical 1-hour deposition (~9,000 words), that's ~450 errors. Those errors include misheard names, numbers, and technical terms — the exact content that matters most in legal/medical work. A human transcriptionist who can pause, rewind, look up context, and clarify unclear moments produces 99%+ accuracy. The remaining 1% is flagged as inaudible rather than guessed at.</p>
<p>For legal depositions, court transcripts, medical records, broadcast captions, FDA hearings, or anything subject to regulation — human transcription is table stakes. Rev is the dominant player; alternatives include GoTranscript, 3Play, Happy Scribe's human tier. AI tools including TranscriptX are not in the running.</p>
<p>The price: $0.25/min = $15/hour of audio. A full-day deposition (6 hours) costs $90. Most AI tools run the same content for under $0.50 in underlying compute — but the accuracy gap is the whole point.</p>

<h2>Rev AI vs TranscriptX — direct competitor</h2>
<p>This is where the comparison gets interesting. Both are AI-based, both handle URL/file input, both are monthly SaaS.</p>
<h3>Pricing</h3>
<p>Rev AI: $14.99/mo for unlimited AI transcription. TranscriptX Pro: $3.99/mo unlimited. Same feature shape, we're 4× cheaper. Rev's pricing reflects their enterprise/legal positioning — they charge more because their brand is associated with human-level accuracy even for AI.</p>

<h3>Accuracy</h3>
<p>Roughly equivalent (~92% for Rev AI, ~95% for us) on our test set. Your mileage will vary by content.</p>

<h3>Subtitle tooling</h3>
<p>Rev has the best subtitle editor on the market — purpose-built for film/video professionals who burn captions into content. SRT, VTT, iTT, all the broadcast formats. We export SRT but our tooling is simpler. If subtitle production is your workflow, Rev's extra cost may be worth it. If you just need text, we're fine.</p>

<h3>Platform coverage</h3>
<p>Rev accepts file uploads and YouTube URLs. TranscriptX handles 1000+ platforms via URL. For wider multi-platform workflows, we win.</p>

<h3>Human-verified upgrade path</h3>
<p>One genuine Rev advantage: if you realize mid-workflow that a specific transcript needs human verification, you can upgrade that file from AI to human for ~$0.25/min. With TranscriptX, you'd need to send the file to a separate human service.</p>

<h2>When AI is good enough</h2>
<p>For most content work, 95% accuracy with a 30-second turnaround beats 99% accuracy with a 24-hour turnaround. Examples where AI transcription is the correct choice:</p>
<ul>
<li>Podcast show notes (you'll edit for flow anyway)</li>
<li>YouTube video summaries</li>
<li>Research interviews for internal analysis (where you're reading for themes, not quoting verbatim)</li>
<li>Content repurposing (transcript → article; AI accuracy is fine, you edit regardless)</li>
<li>Meeting notes (Otter or Notta specifically, but TranscriptX works for recorded calls)</li>
<li>Quick verification of what someone said on video</li>
</ul>
<p>For ~95% of use cases, AI is correct. The 5% that require human transcription know they need it.</p>

<h2>When human transcription is the only answer</h2>
<ul>
<li><strong>Legal depositions and court transcripts</strong> (often legally required to be certified)</li>
<li><strong>Medical records</strong> (HIPAA compliance + regulatory accuracy standards)</li>
<li><strong>Broadcast captioning</strong> (FCC rules mandate specific accuracy)</li>
<li><strong>Published interviews where you'll quote verbatim</strong> (journalistic standards)</li>
<li><strong>Audio evidence in legal proceedings</strong> (chain of custody + guaranteed accuracy)</li>
<li><strong>Academic research where transcripts are submitted as data</strong> (peer review may require human verification)</li>
</ul>
<p>In all of these, the cost of a single error is higher than the cost of human transcription. Rev is the standard. Don't try to save money here.</p>

<h2>Pricing breakdown</h2>
<ul>
<li><strong>Rev Human:</strong> $0.25/min pay-as-you-go. 1-hour audio = $15. Delivered in 12-24 hours.</li>
<li><strong>Rev AI:</strong> $14.99/mo unlimited AI. Includes subtitle editor, SRT/VTT export.</li>
<li><strong>Rev Enterprise:</strong> Custom. SSO, SLA, bulk human transcription discounts.</li>
</ul>
<ul>
<li><strong>TranscriptX Starter:</strong> $1.99/mo, 50 transcripts.</li>
<li><strong>TranscriptX Pro:</strong> $3.99/mo unlimited.</li>
<li><strong>TranscriptX Pro Annual:</strong> $29.99/yr.</li>
</ul>

<h2>TL;DR</h2>
<p>Legal / medical / broadcast → Rev human, period. AI-only use cases → TranscriptX at 1/4 the price of Rev AI. Subtitle production at professional quality → Rev AI for the tooling. Multi-platform URL transcription → TranscriptX for breadth.</p>
""",
        "recommendations": [
            "Don't use AI transcription for anything that could end up in court. The cost of a single mistranscription is higher than 12 hours of waiting for Rev human.",
            "Don't use human transcription for podcasts or content. You're paying 60× more than the use case justifies.",
            "If you're comparing Rev AI to TranscriptX specifically, the differentiator is subtitle tooling (Rev) vs platform coverage + price (us).",
            "For academic research, check your institution's standards. Many now accept AI transcripts with a manual verification pass.",
        ],
        "faq": [
            {
                "q": "How accurate is Rev's human transcription?",
                "a": "99%+ guaranteed. Errors typically come from genuinely unintelligible audio (poor recording, overlapping speech, accents the transcriptionist wasn't trained on) rather than carelessness.",
            },
            {
                "q": "Is AI transcription good enough for my podcast?",
                "a": "Almost certainly yes. Podcasts are edited for flow anyway, so a few AI-level errors get caught in the edit. AI transcription is the correct choice here.",
            },
            {
                "q": "Is Rev AI better than TranscriptX?",
                "a": "Marginally on subtitle-production tooling, equivalent on raw transcription, worse on platform coverage and price. If you need SRT/VTT for broadcast, Rev AI. Otherwise us.",
            },
            {
                "q": "Can I mix AI and human transcription?",
                "a": "With Rev, yes — transcribe everything in AI, upgrade specific files to human as needed. With TranscriptX, you'd do AI here and send the files needing human-grade accuracy to a separate service.",
            },
            {
                "q": "How long does Rev human transcription take?",
                "a": "12-24 hours for standard turnaround. Rush options (2-hour, 4-hour) exist at higher prices. AI transcription at either tool is ~30 seconds to ~10 minutes depending on length.",
            },
            {
                "q": "What does $0.25/min cost for a full podcast?",
                "a": "A 60-minute podcast = $15. A 30-minute podcast = $7.50. If you publish weekly, human transcription is ~$60-100/month — which is why most podcasters use AI.",
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
