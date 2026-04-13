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
            {"q": "Which platforms are supported?", "a": "TranscriptX supports major platforms plus long-tail sources handled by yt-dlp extractors."},
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
        "meta_title": "Best YouTube Transcript Tools (2026) — Feature Comparison",
        "meta_description": "Compare top YouTube transcript tools by workflow speed, accuracy, timestamp quality, and export readiness.",
        "summary": "A buyer-style breakdown to choose the right transcript tool based on output quality and workflow fit.",
        "verdict": "The best choice depends on your workflow. For teams that care about transcript quality and downstream reuse, TranscriptX is the strongest all-around option.",
        "method_note": "Evaluation focuses on real production criteria: URL handling, timestamp fidelity, output quality, and usefulness for content operations.",
        "criteria": [
            {"metric": "Accuracy / readability", "transcriptx": "High-quality Whisper-based transcript output", "alternative": "Ranges from basic captions to acceptable transcript text"},
            {"metric": "Timestamp quality", "transcriptx": "Segment + word-level timing when available", "alternative": "Often segment-only or hidden timing"},
            {"metric": "Platform flexibility", "transcriptx": "YouTube + broader URL coverage", "alternative": "Frequently single-platform scope"},
            {"metric": "Workflow speed", "transcriptx": "Fast extraction to ready-to-edit transcript", "alternative": "Varies; many require extra cleanup"},
            {"metric": "Export usefulness", "transcriptx": "Strong for repurposing and editorial handoff", "alternative": "May require post-processing before use"},
        ],
        "recommendations": [
            "Choose by output quality first, not just UI aesthetics.",
            "For clip scripting and quoting, timestamp fidelity should be a hard requirement.",
            "If transcript output feeds SEO/content ops, prioritize cleaner export over lowest cost.",
        ],
        "faq": [
            {"q": "What is the most important metric when choosing a transcript tool?", "a": "Output quality that survives downstream usage: readability, timestamps, and low cleanup overhead."},
            {"q": "Are free transcript options enough?", "a": "Sometimes. They work for casual use, but teams usually outgrow them when consistency and speed become priorities."},
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
        "meta_title": "Platform Support Index — TranscriptX + yt-dlp Coverage",
        "meta_description": "See supported transcript source platforms and extractor coverage used by TranscriptX.",
        "summary": "Live index of supported source platforms and extraction coverage.",
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
    paths.append("/press-kit")
    return paths
