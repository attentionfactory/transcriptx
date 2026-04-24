import re
import subprocess
from datetime import datetime, timezone
from functools import lru_cache


HEAD_TERM_PAGES = {
    "youtube-transcript-generator": {
        "path": "/youtube-transcript-generator",
        "slug": "youtube-transcript-generator",
        "title": "YouTube Transcript Generator — Free, Fast, Accurate | TranscriptX",
        "description": "Generate accurate YouTube transcripts in 60 seconds. Paste any public URL, preview free, export clean transcript text with word-level timestamps. 95% accuracy on clear audio.",
        "h1": "YouTube Transcript Generator",
        "intro": "Turn any public YouTube video into accurate, editable transcript text. Paste a URL, preview output, then extract full text with timestamps in under a minute.",
        "keyword": "youtube transcript generator",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "body_html": """
<h2>What this tool does</h2>
<p>TranscriptX takes any public YouTube URL and returns a clean, editable transcript with word-level timestamps in under 60 seconds. We use modern AI speech recognition that produces ~95% accuracy on clear audio and ~88% on noisy real-world recordings — measurably better than YouTube's built-in auto-captions on anything other than studio-quality content.</p>
<p>The tool is free to try (3 transcripts per month) and unlimited at $3.99/month. No installs, no extensions, no file uploads — just paste a URL.</p>

<h2>How to generate a YouTube transcript</h2>
<ol>
<li><strong>Copy the YouTube video URL.</strong> Any URL format works — full <code>youtube.com/watch?v=XYZ</code>, shortened <code>youtu.be/XYZ</code>, Shorts URLs, embed URLs.</li>
<li><strong>Paste it into the input field above.</strong></li>
<li><strong>Click "Extract Transcript."</strong> Processing usually takes 30-90 seconds depending on video length.</li>
<li><strong>Read, copy, or export.</strong> Transcript appears with timestamps. Download as TXT, CSV, or JSON.</li>
</ol>
<p>That's the whole flow. If you have an account (free), you also get a downloadable history of every transcript you've generated.</p>

<h2>What makes this better than YouTube's built-in transcript</h2>
<p>YouTube has a built-in transcript option (three-dot menu under any video → "Show transcript"). It's free and works for most public videos. So why pay for a tool?</p>
<ul>
<li><strong>Higher accuracy on real-world audio.</strong> Native captions are ~85% accurate on studio audio, dropping to 65-75% on accented speech, background noise, or technical jargon. Our engine averages 88-95% across the same content. The difference compounds — a 1500-word transcript with 10% errors is 150 words to fix; with 5% it's 75. The cleanup time gap is real.</li>
<li><strong>Word-level timestamps.</strong> YouTube's transcript groups words into caption blocks (every 3-5 seconds). For citing exact moments or extracting clip start/end times, you need word-level precision. We provide both segment and word-level timestamps in the JSON export.</li>
<li><strong>Export formats.</strong> YouTube gives you copy-paste from a sidebar. We export TXT (plain reading), CSV (for spreadsheets and content calendars), and JSON (for programmatic processing or AI summarization).</li>
<li><strong>Works on videos with no captions.</strong> Some YouTube videos don't have auto-captions — newer uploads, channels that disabled them, or unsupported languages. We transcribe directly from audio, so caption availability doesn't matter.</li>
<li><strong>Batch workflows.</strong> Transcribing 20 videos via YouTube's panel = 30 minutes of clicking. With us = paste URLs, get transcripts. The compound time savings is the whole point of the tool.</li>
</ul>
<p>For a one-off "I just want to read this video," YouTube's built-in option is fine. For repeatable workflows, the tool above is built for the job.</p>

<h2>What you can do with a YouTube transcript</h2>
<h3>Repurpose into blog posts and articles</h3>
<p>Every video you publish can become a SEO-ranking article on your website. Transcribe → restructure with H2/H3 headings → expand with context → publish. Most teams that do this systematically get more traffic from Google search of their video content than from YouTube's own recommendations.</p>

<h3>Pull quote clips for social media</h3>
<p>A 30-minute interview contains 5-10 standout 30-90 second moments worth clipping for TikTok, Instagram Reels, or YouTube Shorts. Word-level timestamps let you find the exact start of the quotable moment, not "somewhere in this 4-second caption block."</p>

<h3>Write better video descriptions</h3>
<p>Top-performing YouTube descriptions are 200-400 words with specific keywords from your spoken content. The transcript is where you mine those words — search terms hidden in your own video that you didn't notice.</p>

<h3>Search and reference your back catalog</h3>
<p>"Did I cover X in a video?" becomes a 10-second search of your transcript archive instead of a 10-minute scrub through video. Useful for creators with deep back catalogs and for teams that want to reference their own content efficiently.</p>

<h3>Research and analysis</h3>
<p>Journalists, researchers, and market analysts transcribe other people's YouTube videos for citation and quote extraction. Word-level timestamps make precise citation fast.</p>

<h2>Accuracy: what to expect</h2>
<p>Based on our public <a href="/research/transcription-accuracy-benchmark">benchmark of 25 videos</a> across 5 content types:</p>
<ul>
<li><strong>Scripted explainers (clear studio audio):</strong> 96% accuracy</li>
<li><strong>Podcast-style interviews:</strong> 93%</li>
<li><strong>Noisy outdoor vlogs:</strong> 89%</li>
<li><strong>Technical content with jargon:</strong> 92%</li>
<li><strong>Non-English content:</strong> 91% (Spanish, Japanese, mixed)</li>
</ul>
<p>For comparison, YouTube's native auto-captions averaged 76-89% across the same set. The gap widens on harder content — accented speech, background noise, technical vocabulary — which is where you most need the accuracy.</p>

<h2>Supported video formats and edge cases</h2>
<ul>
<li><strong>YouTube Shorts:</strong> fully supported, paste the Shorts URL like any video.</li>
<li><strong>YouTube Live (after broadcast):</strong> supported once the live stream is archived as a video.</li>
<li><strong>Long videos (1+ hours):</strong> supported but processing takes proportionally longer (a 2-hour video takes ~2-3 minutes).</li>
<li><strong>Members-only videos:</strong> not supported — these require an authenticated session, which external tools can't provide. See our <a href="/help/private-video-transcript">private video help page</a>.</li>
<li><strong>Region-locked videos:</strong> not supported if the video isn't available in our server's region. See our <a href="/help/region-locked-video-transcript">region-locked help page</a>.</li>
<li><strong>Age-restricted videos:</strong> usually not supported (require sign-in). Channel owner can disable the restriction; otherwise download the video while signed in and transcribe the file.</li>
</ul>

<h2>Pricing</h2>
<ul>
<li><strong>Free:</strong> 3 transcripts/month. Test the tool, validate accuracy on your content.</li>
<li><strong>Starter ($1.99/mo):</strong> 50 transcripts/month. Casual workflow.</li>
<li><strong>Pro ($3.99/mo):</strong> Unlimited transcripts. The right answer for any serious workflow.</li>
<li><strong>Pro Annual ($29.99/yr):</strong> Same as Pro, paid yearly. Effectively $2.50/mo.</li>
</ul>
<p>Comparing to alternatives: Otter is $8.33/mo (300 min limit on free), Notta is $8.25/mo (120 min lifetime free), Rev's AI tier is $14.99/mo. Full <a href="/compare/best-youtube-transcript-tools">tool comparison page</a> for context.</p>
""",
        "faq": [
            {"q": "Does this work with YouTube Shorts?", "a": "Yes, Shorts URLs are supported as long as the video is publicly accessible. Paste the Shorts URL the same way as a regular video."},
            {"q": "Can I get timestamps?", "a": "Yes — TranscriptX returns both segment-level and word-level timestamps. Word-level is available in the JSON export and is precise to the millisecond."},
            {"q": "Is there a free tier?", "a": "Yes. Free accounts get 3 transcripts per month, no credit card required. Plenty to validate accuracy on your specific content before paying."},
            {"q": "How accurate is the transcript?", "a": "About 95% on clear audio, dropping to 88-92% on noisy real-world recordings. Higher than YouTube's native auto-captions, which average 70-85% on the same content."},
            {"q": "Can I transcribe a private YouTube video?", "a": "No external tool can — private videos require authentication that we can't provide. If you own the video, change visibility to Unlisted (still hidden from search but reachable by link). Full details on our <a href=\"/help/private-video-transcript\">private video help page</a>."},
            {"q": "What's the longest video TranscriptX can handle?", "a": "Practically no upper limit, though long videos (3+ hours) take proportionally more processing time. We've successfully transcribed 4+ hour podcasts and full conference talks."},
            {"q": "Does this work with non-English videos?", "a": "Yes, 90+ languages with auto-detection. Accuracy is strongest in English, Spanish, French, German, Portuguese, Italian, Japanese, and Korean. Lower-resource languages still work but accuracy varies more."},
            {"q": "How is this different from copying YouTube's auto-captions?", "a": "Higher accuracy on real-world audio, word-level timestamps (vs caption blocks), structured export formats (TXT/CSV/JSON), works on videos without captions, and faster batch workflows. For one-off reads, native captions are fine; for repeatable workflows, this tool wins."},
        ],
    },
    "download-youtube-transcript": {
        "path": "/download-youtube-transcript",
        "slug": "download-youtube-transcript",
        "title": "Download YouTube Transcript — TXT, CSV, JSON Export | TranscriptX",
        "description": "Download a YouTube transcript from any public video URL. Export as TXT, CSV, or JSON with word-level timestamps. No browser extension, no file conversion needed.",
        "h1": "Download YouTube Transcript",
        "intro": "Get a downloadable YouTube transcript in TXT, CSV, or JSON — with timestamps — from any public video URL. Built for content workflows, not just casual reading.",
        "keyword": "download youtube transcript",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "body_html": """
<h2>Why "downloading" a transcript matters</h2>
<p>YouTube's built-in transcript appears in a sidebar panel — you can read it, but you can't download it without copy-pasting and reformatting. For anything beyond casual reading (publishing, repurposing, archiving, programmatic processing), that's a real barrier.</p>
<p>TranscriptX gives you actual file exports: TXT for reading, CSV for spreadsheets, JSON for code. Every export includes word-level timestamps and segment metadata, so the file is useful immediately — no manual cleanup required.</p>

<h2>Export formats explained</h2>
<h3>TXT — plain text for reading</h3>
<p>Clean transcript with paragraph breaks at natural pauses. Useful for reading, pasting into a doc, or feeding to an AI summarizer. Largest file, easiest to consume.</p>
<pre style="background:rgba(255,255,255,0.4);padding:.7rem;border-radius:6px;font-size:.7rem;overflow:auto;">[00:00] Welcome back to the show. Today we're talking about...
[00:08] So let's dive in. The first thing you need to know is...</pre>

<h3>CSV — spreadsheet format</h3>
<p>One row per segment. Columns: start time, end time, text. Drop into Excel, Google Sheets, Airtable, or your content calendar. Useful for tracking what was said when across many videos.</p>
<pre style="background:rgba(255,255,255,0.4);padding:.7rem;border-radius:6px;font-size:.7rem;overflow:auto;">start,end,text
0.00,8.32,"Welcome back to the show. Today we're talking about..."
8.32,15.18,"So let's dive in. The first thing you need to know is..."</pre>

<h3>JSON — programmatic format</h3>
<p>Full structured data: every word with its own start/end timestamp, every segment with metadata. Built for scripts, AI tooling, subtitle production, custom workflows. The most flexible export.</p>
<pre style="background:rgba(255,255,255,0.4);padding:.7rem;border-radius:6px;font-size:.7rem;overflow:auto;">{
  "segments": [{"start": 0.0, "end": 8.32, "text": "Welcome back..."}],
  "words": [{"word": "Welcome", "start": 0.0, "end": 0.42}, ...]
}</pre>

<h2>Download workflow</h2>
<ol>
<li>Paste the YouTube URL above and click "Extract Transcript."</li>
<li>Wait 30-90 seconds for processing.</li>
<li>Click your preferred export format in the result card (TXT, CSV, or JSON).</li>
<li>The file downloads directly to your machine. Filename includes the video title for easy organization.</li>
</ol>

<h2>Common download workflows</h2>
<h3>Subtitle / SRT production</h3>
<p>JSON output contains all the data needed to generate SRT or VTT subtitle files. Convert with any standard SRT generator (ffmpeg-based scripts, online tools, or Descript). Direct SRT export is on our roadmap.</p>

<h3>Content repurposing pipelines</h3>
<p>TXT into your CMS or blog editor. CSV into Notion or Airtable as a content calendar entry. JSON into Claude or ChatGPT to draft articles, social posts, or newsletter copy.</p>

<h3>Archiving and reference</h3>
<p>Download all transcripts to a folder you back up. Future-you will thank past-you when someone asks "didn't you say something about X?" and you can grep your transcript folder in 5 seconds.</p>

<h3>Citation and quote extraction</h3>
<p>For journalism, research, or analysis work — JSON gives word-level timestamps so you can cite exact moments. "At 14:32 of the address, the candidate said..."</p>

<h2>What's NOT included in the download</h2>
<ul>
<li><strong>Speaker labels.</strong> We don't separate speakers into named labels (Otter does this better for multi-person recordings). Our segments group at natural pauses.</li>
<li><strong>The original video file.</strong> We extract audio for transcription only. If you want the video itself, use a downloader like yt-dlp.</li>
<li><strong>Punctuation guarantees.</strong> Auto-punctuation is included but isn't perfect. For published work, do an editorial pass.</li>
</ul>

<h2>Privacy when downloading</h2>
<p>Transcripts are stored against your account so you can re-download or reference them later. We don't share your transcripts or use your content for training. For privacy-critical work where you want zero cloud retention, offline tools like Buzz (open-source, runs locally) are an alternative — slower UX, free, fully offline.</p>

<h2>Pricing</h2>
<ul>
<li><strong>Free:</strong> 3 transcripts/month with full export access.</li>
<li><strong>Starter ($1.99/mo):</strong> 50 transcripts/month. Good for personal workflows.</li>
<li><strong>Pro ($3.99/mo):</strong> Unlimited. The right tier for content workflows that compound.</li>
</ul>
""",
        "faq": [
            {"q": "Do I need subtitles enabled on YouTube?", "a": "No. TranscriptX transcribes audio directly and does not depend on YouTube's caption track. Even videos without captions work."},
            {"q": "Can I clip by highlighted text?", "a": "Yes — selected transcript ranges can be mapped to timestamps for segment downloads. The JSON export contains word-level start/end times for precise clipping."},
            {"q": "What format should I export?", "a": "TXT for reading, CSV for spreadsheets and content calendars, JSON for programmatic processing or feeding to AI tools. Most users export JSON for flexibility, then derive other formats from it."},
            {"q": "Can I download SRT or VTT subtitles?", "a": "Not directly today — our JSON export contains all the timestamp data needed to generate SRT/VTT with any standard converter. Direct export is on the roadmap."},
            {"q": "How long are transcripts kept on my account?", "a": "Indefinitely while your account is active. Re-download anytime."},
            {"q": "Are downloads included in the free tier?", "a": "Yes, all 3 free transcripts per month include full export access — same formats as paid tiers, no watermark."},
            {"q": "Can I batch-download many transcripts?", "a": "Yes via our batch workflow. Paste multiple URLs in the input area and process them sequentially. Each transcript is downloadable individually."},
            {"q": "Does the download include speaker labels?", "a": "No, we don't separate speakers into named labels. For multi-person recordings where speaker labels matter, Otter handles diarization better than we do."},
        ],
    },
    "youtube-to-transcript": {
        "path": "/youtube-to-transcript",
        "slug": "youtube-to-transcript",
        "title": "YouTube to Transcript Converter — URL to Text in 60 Seconds | TranscriptX",
        "description": "Convert YouTube video URLs into editable transcripts with AI. 95% accuracy, 90+ languages, word-level timestamps, exports as TXT/CSV/JSON. Built for content and research teams.",
        "h1": "YouTube to Transcript",
        "intro": "Paste a YouTube URL and convert spoken audio to readable text you can publish, quote, search, or feed to AI in 60 seconds.",
        "keyword": "youtube to transcript",
        "platform": "YouTube",
        "cta_label": "Extract Transcript",
        "body_html": """
<h2>Why convert YouTube to transcript?</h2>
<p>Video is great for consumption — bad for reference. You can't search a video. You can't easily quote it. You can't paste it into another document or feed it to an AI tool. Converting YouTube content to transcript text unlocks all of that, fast.</p>
<p>For most workflows the value is one of:</p>
<ul>
<li><strong>Search and reference:</strong> find specific moments in long videos without scrubbing</li>
<li><strong>Repurposing:</strong> turn one video into a blog post, newsletter, social clips, or sales doc</li>
<li><strong>Analysis:</strong> feed transcripts into AI tools for summarization, theme extraction, or fact-checking</li>
<li><strong>Citation:</strong> quote video content with timestamps in articles, papers, or research</li>
</ul>
<p>TranscriptX does this conversion in 60 seconds with ~95% accuracy on clear audio. No file uploads, no extensions — paste the URL and you're done.</p>

<h2>Three workflows people actually use</h2>

<h3>Conversion for content repurposing</h3>
<p>You publish a video. Within an hour, transcribe it and feed it to Claude or ChatGPT with a prompt like "turn this transcript into a 1000-word article with 5 subheadings." First draft comes back in 30 seconds. Edit for 30 minutes, publish. The video that exists on YouTube now also exists as a SEO-ranking article on your website. Compound this across every video you publish, and the website becomes the primary traffic channel within 12-18 months.</p>

<h3>Conversion for research and quoting</h3>
<p>Transcribe a video you want to cite. Use the word-level timestamps in JSON to identify the exact start of the quote you want to use. Cite as "[time] in [video title], [speaker] said..." with a link to the YouTube URL. Faster and more accurate than re-scrubbing the video to find the moment.</p>

<h3>Conversion for batch analysis</h3>
<p>Transcribe 20 competitor videos in a batch. Drop transcripts into a searchable document store (Notion, Airtable, Google Docs). Search across all 20 for specific topics, claims, or terminology. Build a competitive intelligence asset from public content other teams aren't bothering to mine.</p>

<h2>Conversion accuracy</h2>
<p>From our published <a href="/research/transcription-accuracy-benchmark">benchmark</a> across 25 real videos:</p>
<table style="width:100%;border-collapse:collapse;font-size:.78rem;background:rgba(255,255,255,0.4);">
<thead><tr style="background:rgba(0,0,0,0.08);"><th style="padding:.4rem;text-align:left;border:1px solid rgba(0,0,0,0.15);">Content type</th><th style="padding:.4rem;text-align:left;border:1px solid rgba(0,0,0,0.15);">TranscriptX</th><th style="padding:.4rem;text-align:left;border:1px solid rgba(0,0,0,0.15);">YouTube native</th></tr></thead>
<tbody>
<tr><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">Scripted explainer</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">96%</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">89%</td></tr>
<tr><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">Podcast interview</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">93%</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">81%</td></tr>
<tr><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">Noisy vlog</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">89%</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">72%</td></tr>
<tr><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">Technical jargon</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">92%</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">68%</td></tr>
<tr><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">Spanish / Japanese</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">91%</td><td style="padding:.4rem;border:1px solid rgba(0,0,0,0.15);">78%</td></tr>
</tbody>
</table>
<p>The gap matters most on noisy and technical content — exactly where you most need accuracy and where YouTube's native auto-captions struggle.</p>

<h2>Speed</h2>
<p>Conversion typically takes 30-90 seconds for videos up to 30 minutes. A 2-hour podcast might take 2-3 minutes end-to-end. We process audio in parallel with multiple AI engines for speed; total time is dominated by audio download from YouTube, not the transcription itself.</p>

<h2>What about non-English videos?</h2>
<p>90+ languages supported with automatic detection. The model handles English, Spanish, French, German, Portuguese, Italian, Japanese, Korean, Mandarin, Arabic, Russian, Turkish, Hindi, Vietnamese, Thai, Indonesian, Malay, Polish, Dutch, Swedish — basically all the languages with substantial training data. Less-common languages (Welsh, Basque, Tagalog regional dialects) still work but accuracy varies.</p>
<p>For multilingual content (code-switching mid-sentence), accuracy drops modestly. Tools that lock into one language and transcribe the other phonetically will produce garbage on these — we generally do better but it's still the hardest case.</p>

<h2>Privacy and ownership</h2>
<p>Transcripts are stored against your account for re-download. We don't use your content for AI training. For ownership-sensitive work (other people's copyrighted videos, sensitive customer interviews), check our terms.</p>

<h2>Pricing</h2>
<ul>
<li><strong>Free:</strong> 3/month, all features included.</li>
<li><strong>Starter ($1.99/mo):</strong> 50/month.</li>
<li><strong>Pro ($3.99/mo):</strong> Unlimited.</li>
<li><strong>Pro Annual ($29.99/yr):</strong> Same as Pro, ~$2.50/mo effective.</li>
</ul>
""",
        "faq": [
            {"q": "How accurate is conversion?", "a": "About 95% on clear audio, 88-92% on noisy real-world recordings. Higher than YouTube's native auto-captions across every content type we've tested. Full numbers in our <a href=\"/research/transcription-accuracy-benchmark\">benchmark</a>."},
            {"q": "Can I process long videos?", "a": "Yes. Practically no upper limit. A 1-hour video processes in 60-90 seconds; a 4-hour podcast in 3-5 minutes. The model handles long-form fine."},
            {"q": "What languages are supported?", "a": "90+ with automatic detection. English, Spanish, French, German, Portuguese, Italian, Japanese, Korean, Mandarin, Arabic, Russian, Turkish, Hindi, Vietnamese, Thai — all the major languages with substantial training data."},
            {"q": "Does it work on YouTube Shorts?", "a": "Yes, paste the Shorts URL like any video."},
            {"q": "Is my video data used for AI training?", "a": "No. We don't use your content to train models. Transcripts are stored only so you can re-download them."},
            {"q": "Can I convert from a YouTube playlist URL?", "a": "Currently you paste each video URL individually. Playlist-batch is on the roadmap. For now, our manual batch input handles up to 10 URLs at once on paid tiers."},
            {"q": "Does the conversion include speaker labels?", "a": "No, we don't add named speaker labels. Otter handles speaker diarization better for multi-person recordings."},
            {"q": "Can I use this for offline analysis?", "a": "Yes — export as JSON or TXT, then use offline. The transcript file is yours to keep, search, or feed into other tools."},
        ],
    },
    "video-to-transcript": {
        "path": "/video-to-transcript",
        "slug": "video-to-transcript",
        "title": "Video to Transcript — 1000+ Platforms Supported | TranscriptX",
        "description": "Convert online videos to transcript text from YouTube, TikTok, Instagram, Reddit, Vimeo, LinkedIn, Twitch, SoundCloud, and 1000+ more platforms by pasting a link.",
        "h1": "Video to Transcript",
        "intro": "Use one transcript pipeline for videos across every major platform. Paste any supported URL and get a clean transcript with word-level timestamps in 60 seconds.",
        "keyword": "video to transcript",
        "platform": "Multi-platform",
        "cta_label": "Extract Transcript",
        "body_html": """
<h2>Why the number of sites we cover matters</h2>
<p>Most transcription tools handle one or two platforms. YouTube-only tools work great if all your content is on YouTube. The moment you also need to transcribe a TikTok, Instagram Reel, Vimeo video, LinkedIn post with embedded video, Reddit-hosted clip, SoundCloud track, or a Zoom recording uploaded to Drive — you're back to a different tool, a different workflow, a different export format.</p>
<p>TranscriptX handles 1000+ platforms by pasting a single link. Same accuracy, same export formats, same workflow. This is the actual moat of the product — not "we have AI" (everyone does) but "we handle the platform diversity that real workflows actually have."</p>

<h2>Platforms covered</h2>
<p>The full list lives at our <a href="/research/platform-support-index">full list of sites we support</a> with all 1000+ entries. The major ones:</p>
<ul>
<li><strong>Video sites:</strong> YouTube, Vimeo, TikTok, Instagram, Facebook, X (Twitter), Reddit, LinkedIn, Twitch, Dailymotion</li>
<li><strong>Streaming services:</strong> BBC iPlayer (region-permitting), Hulu, Crunchyroll, Niconico, Bilibili, many regional broadcasters</li>
<li><strong>Audio platforms:</strong> SoundCloud, Bandcamp, Mixcloud, podcast hosts (Apple, Spotify, Amazon)</li>
<li><strong>Cloud storage:</strong> Google Drive (with public-link sharing), Dropbox (with <code>?dl=1</code>), OneDrive (sometimes)</li>
<li><strong>Educational:</strong> Coursera, edX, Khan Academy, YouTube EDU, Vimeo educational channels</li>
<li><strong>Enterprise video:</strong> Wistia, Vidyard, Brightcove, Kaltura (viewer page URLs)</li>
<li><strong>News and politics:</strong> C-SPAN, Reuters, AP, broadcaster archives</li>
<li><strong>Long-tail:</strong> regional video services, Telegram, Discord recordings (with public links), niche platforms most tools have never heard of</li>
</ul>

<h2>How the multi-platform workflow saves time</h2>
<p>Consider a marketing team that publishes content across 4 platforms (YouTube long-form, TikTok shorts, LinkedIn videos, Vimeo for client work). Without multi-platform support:</p>
<ul>
<li>YouTube: built-in panel (manual) or Tool A (paid sub)</li>
<li>TikTok: download video manually, upload to Tool B (paid sub) or Drive</li>
<li>LinkedIn: similar manual flow with Tool C</li>
<li>Vimeo: yet another tool</li>
</ul>
<p>Three subscriptions, three workflows, three different export formats to merge. With TranscriptX: one subscription, one workflow, one export format. The compound time savings is the entire reason multi-platform tools win for serious workflows.</p>

<h2>Common multi-platform use cases</h2>
<h3>Cross-platform competitive analysis</h3>
<p>You want to track what competitors say across YouTube, TikTok, LinkedIn, and podcast appearances. Each platform requires a different download/upload dance with most tools. With us: paste each URL, get transcripts, search across all of them.</p>

<h3>Multi-format content repurposing</h3>
<p>Your team publishes long-form on YouTube, short-form on TikTok and Reels, podcast on Spotify. Every piece can become other content via transcription — but only if transcribing each is fast. Multi-platform support is what makes the cross-format repurposing actually viable.</p>

<h3>Research from diverse video sources</h3>
<p>Academic and journalistic research increasingly cites video content from many platforms. A research paper on social media discourse might quote TikToks, YouTube videos, Twitter Spaces recordings, and LinkedIn posts. Transcribing each in a different tool with different formats is friction; one tool handling all of them is reasonable.</p>

<h3>Customer/competitor insights from social</h3>
<p>Brand monitoring teams transcribe TikToks/Reels mentioning their brand or competitor brands. Without multi-platform tools this is too painful to do regularly. With them, it becomes a routine weekly workflow.</p>

<h2>What about platforms we don't list?</h2>
<p>The 1000+ count is impressive but not exhaustive. If a platform isn't in our index:</p>
<ol>
<li><strong>Try the URL anyway.</strong> Our generic extractor handles many sites we don't formally list — if the video plays in a standard browser without login, we usually transcribe it.</li>
<li><strong>If it fails:</strong> download the video to your machine, upload to Google Drive with public-link sharing, paste the Drive URL. See our <a href="/help/upload-audio-file-transcript">file upload help page</a>.</li>
<li><strong>For private platforms (Discord, Slack, Zoom):</strong> we can't reach authentication-gated content. Workaround is the same — record/export, upload, paste URL.</li>
</ol>

<h2>Pricing for multi-platform workflows</h2>
<ul>
<li><strong>Free:</strong> 3/month — enough to validate the tool on whatever mix of platforms you use.</li>
<li><strong>Starter ($1.99/mo):</strong> 50/month. Casual cross-platform work.</li>
<li><strong>Pro ($3.99/mo):</strong> Unlimited. Right tier for any team that's serious about multi-platform content workflows.</li>
</ul>
""",
        "faq": [
            {"q": "Which platforms are supported?", "a": "1000+ — see our <a href=\"/research/platform-support-index\">full list of sites we support</a> for the complete list. Major platforms include YouTube, TikTok, Instagram, Vimeo, X (Twitter), Facebook, Reddit, LinkedIn, Twitch, SoundCloud."},
            {"q": "Can teams export data?", "a": "Yes — TXT, CSV, JSON exports. JSON includes word-level timestamps for programmatic use; CSV drops into Notion, Airtable, or Excel cleanly."},
            {"q": "What if my platform isn't in the list?", "a": "Try the URL anyway — our generic extractor handles many unlisted platforms. If it fails, the workaround is to upload the video to Google Drive with public sharing and paste the Drive URL."},
            {"q": "Does this work on TikTok and Instagram?", "a": "Yes for both, by pasting a link directly. Reels and TikTok videos work reliably; Instagram Stories are harder due to their auth-gated, ephemeral nature — see our <a href=\"/help/instagram-story-transcript\">Story-specific help page</a>."},
            {"q": "Can I transcribe a Zoom recording?", "a": "Yes if you upload it to Google Drive (or similar) with public link sharing first, then paste the Drive URL. We don't currently join live Zoom calls — for live capture use Otter."},
            {"q": "What about region-locked content?", "a": "If the video isn't available in our server's region, we can't reach it. Workarounds in our <a href=\"/help/region-locked-video-transcript\">region-lock help page</a>."},
            {"q": "Are private videos supported?", "a": "Not without authentication. Most external tools have this same limitation. See our <a href=\"/help/private-video-transcript\">private video help page</a> for the workarounds."},
            {"q": "Is multi-platform support more expensive?", "a": "No, same pricing applies regardless of platform. Pro at $3.99/mo gives you unlimited transcripts across every supported platform."},
        ],
    },
    "audio-to-transcript": {
        "path": "/audio-to-transcript",
        "slug": "audio-to-transcript",
        "title": "Audio to Transcript — Convert Podcasts, Recordings, Voice Notes | TranscriptX",
        "description": "Convert audio to clean transcript text from podcasts, voice recordings, MP3 files, and audio-only video URLs. 95% accuracy, 90+ languages, word-level timestamps.",
        "h1": "Audio to Transcript",
        "intro": "TranscriptX extracts audio from supported video URLs (and audio-only URLs) and converts speech to clean transcript text in under a minute.",
        "keyword": "audio to transcript",
        "platform": "Audio from video URLs",
        "cta_label": "Extract Transcript",
        "body_html": """
<h2>Audio is the input; text is the output</h2>
<p>Whether your source is a podcast episode, a voice memo, a YouTube video, a Zoom recording, or any audio-bearing file — transcription is the same job: turn speech into text you can read, search, edit, or feed to other tools.</p>
<p>TranscriptX handles audio in two main ways:</p>
<ol>
<li><strong>From any video URL:</strong> we extract the audio track automatically. You don't need to convert MP4 to MP3 first.</li>
<li><strong>From any public audio URL:</strong> SoundCloud, podcast feeds (Apple, Spotify, RSS), Bandcamp, Mixcloud, or any direct MP3/WAV link.</li>
</ol>
<p>For local audio files (MP3 on your laptop, voice memo on your phone), upload to Google Drive with "Anyone with the link" sharing first, then paste the Drive URL. See our <a href="/help/upload-audio-file-transcript">file upload help page</a>.</p>

<h2>Audio sources we handle well</h2>
<h3>Podcasts</h3>
<p>Apple Podcasts, Spotify, SoundCloud, your own RSS feed — paste the episode URL. Most podcast hosts (Transistor, Buzzsprout, Castos) expose direct episode URLs that we can fetch from. Useful for show notes generation, episode repurposing, and quote extraction.</p>

<h3>Voice memos and recordings</h3>
<p>Phone voice memos, dictated notes, recorded interviews — upload to Drive/Dropbox with public sharing, paste the URL. Our engine handles single-speaker voice content very well (~95% accuracy).</p>

<h3>Conference talks and lectures</h3>
<p>Audio recordings of talks, often without video, are ideal for our pipeline — clean speech, single speaker, structured content. Accuracy here is among the highest of any content type.</p>

<h3>Music with vocals</h3>
<p>If you want lyrics from a song, this works in principle but accuracy drops significantly because the model is tuned for speech, not singing. For lyric transcription, dedicated tools usually do better.</p>

<h3>Multi-speaker recordings</h3>
<p>Conference panels, interviews, group discussions — all transcribe but we don't separate speakers into named labels. For that, Otter's diarization is better.</p>

<h2>Workflow: audio to transcript in under 2 minutes</h2>
<ol>
<li><strong>Find the audio source URL.</strong> Could be a podcast episode link, a SoundCloud track, a Drive file, a YouTube video (we'll extract audio), or any direct MP3/WAV link.</li>
<li><strong>Paste into the input above.</strong></li>
<li><strong>Click "Extract Transcript."</strong> Processing usually completes in 30-90 seconds, even for hour-long content.</li>
<li><strong>Read, copy, or export.</strong> Same TXT/CSV/JSON exports as video transcripts.</li>
</ol>

<h2>Audio quality and accuracy</h2>
<p>Transcript accuracy depends heavily on input audio quality:</p>
<ul>
<li><strong>Studio-quality recordings (clean podcast, voiceover):</strong> 96%+ accuracy.</li>
<li><strong>Phone calls (compressed audio, sometimes noisy):</strong> 88-92%.</li>
<li><strong>Field recordings (background noise, distance from mic):</strong> 80-88% depending on noise level.</li>
<li><strong>Voice memos with wind or traffic:</strong> can drop below 80%.</li>
<li><strong>Multiple speakers overlapping:</strong> drops accuracy on the overlapping moments specifically.</li>
</ul>
<p>For mission-critical work where accuracy matters more than speed (legal depositions, medical records), human transcription via Rev is still the standard. AI gets you to 95%; human gets you to 99%+. The 4-point gap matters when the cost of error is high.</p>

<h2>Common audio workflows</h2>
<h3>Podcast show notes</h3>
<p>Transcribe episode → extract 5-8 quotes worth highlighting → write 2-3 sentence summary → publish as show notes. 30 minutes of work; without transcription, 2-3 hours.</p>

<h3>Interview transcription for journalism or research</h3>
<p>Record interview (Zoom, phone recorder, in-person device). Upload audio to Drive with public link. Paste URL. Get transcript. Verify direct quotes against the audio. Cite with timestamps.</p>

<h3>Voice notes to action items</h3>
<p>Record voice notes during walks/commutes. Upload + transcribe. Paste transcript into Claude with "extract action items" prompt. End result: voice memo becomes structured to-do list.</p>

<h3>Audio archive search</h3>
<p>Old podcasts, recorded lectures, voice memos from years ago — transcribe and store as searchable text. "Did I record a thought about X?" becomes a 5-second grep.</p>

<h2>Privacy for sensitive audio</h2>
<p>Voice recordings often contain sensitive content. Our infrastructure processes audio without retaining files beyond the transcription pass, and we don't use audio for training. For maximum privacy on highly sensitive content (medical, legal, personal), offline tools like Buzz let you run the same class of AI model locally on your machine — slower UX, free, fully offline.</p>

<h2>Pricing</h2>
<ul>
<li><strong>Free:</strong> 3 audio transcripts/month.</li>
<li><strong>Starter ($1.99/mo):</strong> 50/month.</li>
<li><strong>Pro ($3.99/mo):</strong> Unlimited. Best fit for podcasters and anyone with regular audio transcription needs.</li>
</ul>
""",
        "faq": [
            {"q": "Do I need to download MP3 first?", "a": "No. TranscriptX handles audio extraction internally from URL input. Paste a YouTube/Vimeo/podcast URL directly — we extract the audio automatically."},
            {"q": "Does it support multiple languages?", "a": "Yes — 90+ languages with automatic detection. Strongest in English, Spanish, French, German, Portuguese, Italian, Japanese, Korean, Mandarin, and Arabic."},
            {"q": "Can I transcribe a podcast episode from Spotify?", "a": "Yes for publicly available episodes — paste the Spotify episode URL. Same for Apple Podcasts, SoundCloud, and most RSS-distributed podcasts."},
            {"q": "What about voice memos from my phone?", "a": "Upload to Google Drive with \"Anyone with the link\" sharing, then paste the Drive file URL. See our <a href=\"/help/upload-audio-file-transcript\">file upload help page</a> for the exact steps."},
            {"q": "What audio file formats work?", "a": "Common ones — MP3, M4A, WAV, OGG, AAC, FLAC. If it plays in standard media players, it usually works for us."},
            {"q": "How long can the audio be?", "a": "Practically no upper limit, though long audio (3+ hours) takes proportionally more processing. We've successfully transcribed 4+ hour podcasts."},
            {"q": "Does this work for multi-speaker conversations?", "a": "Transcription works fine; we don't separate speakers into named labels though. For multi-person recordings where labels matter, Otter's diarization is better."},
            {"q": "Can I get accurate transcripts of music lyrics?", "a": "In principle yes, but our engine is tuned for speech, not singing — accuracy on music drops significantly. For lyric transcription, dedicated lyric tools usually do better."},
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
        "intro": "Extract transcript-ready text from X video posts for writing and editing and quote capture.",
    },
    "x-twitter": {
        "display": "X (Twitter)",
        "intro": "Extract transcript-ready text from X video posts for writing and editing and quote capture.",
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
                "pick": "TranscriptX. This is our actual moat — we handle 1000+ platforms by pasting a single link. Every other tool here is YouTube-only, meetings-only, or requires manual file upload.",
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
<p><strong>Where we win:</strong> the number of sites we cover. We handle 1000+ sources — YouTube, TikTok, Instagram, X, Reddit, Vimeo, LinkedIn, Twitch, SoundCloud, and a long tail of regional streaming services. Paste any public video URL and we extract the audio and transcribe it. No upload, no file conversion, no "install this extension first."</p>
<p>Our engine handles noisy real-world audio, accents, and technical vocabulary better than YouTube's native auto-captions. Word-level and segment-level timestamps are returned by default, and the output is structured for repurposing (CSV/JSON export, not just copy-paste).</p>
<p><strong>Where we lose:</strong> we don't do live meetings (use Otter), we don't replace your video editor (use Descript), and we don't do human-verified transcripts (use Rev). Our API is on the roadmap but not shipped yet.</p>
<p><strong>Use it when:</strong> you transcribe public videos and podcasts across more than one platform, you want cheap unlimited usage ($3.99/mo), and you care about exportable, timestamped output.</p>

<h3>Otter.ai — the meeting notes tool</h3>
<p>Otter isn't really a transcript tool; it's a meeting assistant. It joins your Zoom/Google Meet/Teams calls as a bot, transcribes the whole meeting in real-time with speaker attribution, and dumps shared notes into your team's workspace. For that use case it's excellent.</p>
<p>You <em>can</em> upload YouTube audio to Otter and get a transcript out, but it's not the path of least resistance — the tool's UX is optimized around meetings, not public videos and podcasts. Accuracy is good (~90% on clear audio). Integrations with Slack, Notion, and Salesforce are best-in-class. Pricing is $8.33/mo annually with a generous 300-min free tier.</p>
<p><strong>Use it when:</strong> team meetings are the unit of work. Skip if your content is videos from a link.</p>

<h3>Descript — the transcript-as-editor</h3>
<p>Descript is a video/audio editor where the transcript IS the timeline. Delete a word in the transcript, the corresponding audio gets cut. Move a paragraph, the footage moves. If you're editing podcasts or YouTube essays, this is transformative. If you just want a transcript, it's overkill.</p>
<p>Accuracy is ~92% on clear audio. The "Overdub" feature lets you clone your voice to fix mistakes in the transcript without re-recording. Export includes video, audio, SRT/VTT, and the full edited timeline.</p>
<p><strong>Use it when:</strong> your actual goal is editing — transcription is a byproduct. Skip if you just want text.</p>

<h3>Notta — middle-of-the-road multi-source</h3>
<p>Notta sits between Otter and TranscriptX functionally: multi-source transcription (including YouTube URLs), some live meeting support, solid export options. Accuracy hovers around 89% on clear audio. The free tier is stingy at 120 minutes total (not per month), so it's more of a "try before you buy" than a usable free plan.</p>
<p><strong>Use it when:</strong> you want a single tool that does both meetings and transcribing from a link moderately well, and Otter's meeting-centric UX feels wrong.</p>

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
<li><strong>TranscriptX</strong> if you transcribe public videos and podcasts across multiple platforms and want cheap, fast, exportable output. (Yes we're biased.)</li>
<li><strong>Otter</strong> if most of your content is live meetings and you want notes dropped into your team's workspace automatically.</li>
</ol>
<p>Everything else on this list is a specialist tool that's the right answer for a narrow use case. If you're in that narrow use case, you already know it. If you're not, pick from the three above.</p>
""",
        "recommendations": [
            "Pick by use case, not marketing copy. Every tool on this list is 'best' for someone — the question is whether that someone is you.",
            "Don't over-index on accuracy percentages. The difference between 89% and 92% matters less than whether the tool supports your platform and workflow.",
            "For anything legal or compliance-related, pay for human transcription. AI tools at 95% still produce 5 errors per hundred words — in a 10,000-word deposition that's 500 mistakes.",
            "If your bottleneck is 'I transcribe from 8 different platforms', stop trying to make meeting-centric tools work for public videos and podcasts. That's what we built TranscriptX to solve.",
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
                "a": "TranscriptX handles all three (and 1000+ more platforms) by pasting a link. Otter, Notta, and Happy Scribe require you to download the video first and upload the file — which is fine but adds friction. YouTube CC only works on YouTube. Descript requires file upload.",
            },
            {
                "q": "Which tool has the best free tier?",
                "a": "Otter's 300 minutes/month free is the most generous for live meetings. For transcribing from a link, TranscriptX's 3/month free tier plus YouTube's native CC cover most one-off use cases together.",
            },
            {
                "q": "Which tool has the best API?",
                "a": "For production transcription pipelines, you probably don't want a consumer tool. AssemblyAI, Deepgram, and Rev all have production-grade APIs. Our API is on the roadmap but we'd steer you to one of the above today.",
            },
            {
                "q": "How do I pick between TranscriptX and Otter?",
                "a": "If your content is link-based (YouTube, TikTok, Instagram, etc.), TranscriptX. If your content is live meetings (Zoom, Meet, Teams), Otter. If both, either works as a starting point — add the second tool when you hit the first tool's limits.",
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
        "meta_description": "Otter is built for live meetings. TranscriptX is built for transcribing videos from a link. A direct comparison of both — pricing, accuracy, workflows, and which one you should actually pay for.",
        "summary": "Otter and TranscriptX solve different problems but buyers keep comparing them. Here's a direct side-by-side — where Otter clearly wins (meetings, team workflows, integrations) and where TranscriptX does (videos from a link, the number of sites we cover, pricing per transcription).",
        "verdict": "If your bottleneck is live meetings, buy Otter. If your bottleneck is transcribing videos from YouTube, TikTok, Instagram, Vimeo, Zoom recordings, and other URL sources, buy TranscriptX. If it's both — buy both. They're cheap and solve genuinely different problems.",
        "method_note": "Both tools were tested on the same 15 inputs: 5 Zoom recordings, 5 YouTube videos, 5 TikTok/Instagram clips. For Otter, files were uploaded; for TranscriptX, URLs were pasted. Pricing and limits reflect April 2026 public tiers.",
        "matrix_columns": [
            "Starting price",
            "Accuracy",
            "Live meeting capture",
            "Paste a YouTube, TikTok, or other link",
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
                "pick": "TranscriptX. Otter can technically handle YouTube on paid tiers but you upload the audio or paste links one at a time — it's not the path of least resistance. We built the paste-a-link flow as the core use case.",
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
<h3>Transcribing videos from a link</h3>
<p>Paste a YouTube URL, TikTok link, Instagram Reel, Vimeo video, LinkedIn post with video, Reddit-hosted clip, SoundCloud track, or any of 1000+ other sources. We extract the audio and transcribe it in one step. No download, no upload, no "first export this to an MP4, then..."</p>
<p>Otter can handle YouTube URLs on paid tiers, but the workflow is slower (you paste the URL in a dialog, Otter pulls the audio, transcribes, then the result sits in your workspace). For other platforms like TikTok or Instagram, you generally download the video yourself first, then upload the file — adding 2-3 steps to what should be one.</p>
<p>If the bulk of your transcription is link-based public video content, TranscriptX is the right-shaped tool. It's what we built it for.</p>

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
            "Don't force-fit Otter onto public videos and podcasts workflows. You'll keep hitting 'this is the wrong shape' friction.",
            "Don't force-fit TranscriptX onto live meetings. Record the Zoom file and send it somewhere we can reach, or just use Otter.",
            "For podcasts published to YouTube/SoundCloud, TranscriptX by pasting a link is the fastest path to show notes.",
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
                "a": "Otter's 300 min/mo is more generous than our 3 transcripts/mo if your use case is meetings. Ours makes more sense if you're evaluating transcribing from a link and want to try a few different platforms.",
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
            "Paste a YouTube, TikTok, or other link",
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
<h3>Paste a link from 1000+ platforms</h3>
<p>Descript requires file upload. If you want to transcribe a YouTube video with Descript, you download the video yourself first, then upload the file to Descript, then wait for it to process. TranscriptX: paste URL, get transcript. For any workflow where the source is already online, this matters.</p>

<h3>Price per transcription</h3>
<p>$1.99-3.99/mo vs Descript's $12/mo. If you don't need video editing, paying $12/mo for transcription is buying a power tool to hammer a nail. Descript knows this — their free tier is 1 hour/month, small enough to push serious users into paid.</p>

<h3>Speed to transcript</h3>
<p>Descript is Electron-based and processes media locally. A 30-minute podcast takes 5-10 minutes to transcribe. TranscriptX processes cloud-side and completes the same file in ~60 seconds. If you need 20 transcripts fast, this compounds.</p>

<h3>Bulk / batch workflows</h3>
<p>TranscriptX supports batch link pasting natively. Descript's batch workflow involves queuing projects which takes longer.</p>

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
            "For public videos and podcasts at scale, Descript's upload step is genuine friction. TranscriptX is faster end-to-end.",
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
                "a": "Depends on scope. Recording + editing + publishing → Descript is unrivaled. 'Just show notes from an episode I already published' → TranscriptX by pasting a link is 3× cheaper and faster.",
            },
        ],
    },
    "transcriptx-vs-notta": {
        "slug": "transcriptx-vs-notta",
        "title": "TranscriptX vs Notta",
        "meta_title": "TranscriptX vs Notta — Which Transcription Tool Fits Your Workflow? (2026)",
        "meta_description": "Notta and TranscriptX both do transcribing from a link. Honest comparison of pricing, accuracy, platform coverage, and which one wins for which use case.",
        "summary": "Notta and TranscriptX are the most directly overlapping tools in our comparison set — both handle transcribing videos from a link at similar price points. The differences come down to the number of sites we cover, free-tier generosity, and accuracy on edge cases.",
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
                "persona": "You want the cheapest unlimited option for videos from a link",
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
<li>Accept a pasted link for video transcription</li>
<li>Produce transcripts with timestamps</li>
<li>Export to common formats</li>
<li>Price in the $5-15/mo consumer range</li>
</ul>
<p>The differences are in the specifics: the number of sites we cover, free-tier generosity, accuracy on noisy audio, and pricing tiers.</p>

<h2>Where TranscriptX wins</h2>
<h3>Platform breadth (1000+ vs a handful)</h3>
<p>Notta officially supports YouTube, Zoom, Google Meet, Teams, and a "general upload" path. If you paste a TikTok URL, Instagram Reel, Reddit video, Vimeo link, SoundCloud track, or any of the 1000+ smaller sites we support, Notta's answer is "download it yourself and upload the file."</p>
<p>If your workflow is YouTube-only, Notta's breadth is sufficient. If you touch multiple platforms in a given week, TranscriptX is significantly less friction.</p>

<h3>Unlimited pricing</h3>
<p>TranscriptX Pro at $3.99/mo is unlimited with fair-use. Notta's comparable unlimited is on their Business tier at $16.66/mo annual — 4× the price. If your usage is above a few hundred minutes/month, we're meaningfully cheaper.</p>

<h3>Accuracy on noisy/accented content</h3>
<p>On our 20-video test set, we scored ~6-7 percentage points higher on noisy real-world audio and accented speech. On studio-quality audio the gap narrows to ~5 points. Both are competent tools; the gap only matters if your content is noisy or non-US English.</p>

<h3>Word-level timestamps</h3>
<p>Our output includes both segment and word-level timestamps by default. Notta provides segment-level; word-level is available but less prominent. For clip-highlighting workflows, ours is easier.</p>

<h2>Where Notta wins</h2>
<h3>Live meeting capture</h3>
<p>Notta has a meeting bot that auto-joins Zoom, Google Meet, and Teams, similar to Otter. We don't. If live capture matters, Notta's versatility is real — one tool does both transcribing from a link AND meeting capture, which is a coherent offering.</p>

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
                "a": "Not natively as of April 2026. You download the video yourself, then upload the file. TranscriptX handles both — just paste the link.",
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
            "Paste a link",
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
    "private-video-transcript": {
        "slug": "private-video-transcript",
        "title": "Why Private YouTube Videos Can't Be Transcribed (and What to Do)",
        "meta_title": "Transcribe Private YouTube Video — Why It Fails & Fixes | TranscriptX",
        "meta_description": "If TranscriptX says 'This video is private,' we genuinely can't reach it — no tool can transcribe a private URL without being logged in. Here's what works instead.",
        "intent": "User pasted a private or unlisted YouTube URL and got a 'private video' error.",
        "tldr": "Private videos require a logged-in session that only has permission on accounts you've shared with. No external tool (ours or any competitor) can transcribe a truly private video — it'd have to impersonate you. If you own the video, change visibility to Unlisted (still unlisted to strangers, but reachable via link). If someone else owns it, ask them to make it Unlisted or download it for you.",
        "body_html": """
<h2>What counts as "private"</h2>
<p>YouTube has three visibility levels and the word "private" means something specific:</p>
<ul>
<li><strong>Public</strong> — anyone can find and watch. Transcribable.</li>
<li><strong>Unlisted</strong> — not findable in search or recommendations, but anyone with the link can watch. <strong>Transcribable.</strong></li>
<li><strong>Private</strong> — only explicitly invited Google accounts can watch. Requires login. <strong>Not transcribable.</strong></li>
</ul>
<p>"Unlisted" is often what people mean when they say "private." If the video is Unlisted, we handle it normally — paste the link and it works.</p>

<h2>Why private videos are unreachable</h2>
<p>When you watch a private video, YouTube verifies your Google account was explicitly invited. TranscriptX fetches videos anonymously, the same way a logged-out browser would — and a logged-out browser hits a sign-in wall on private videos. No amount of retrying gets past this. Same thing happens with Otter, Descript, Notta, or any other tool that doesn't authenticate against your Google account.</p>
<p>The only tools that can transcribe private videos are either (a) YouTube itself, because you're logged in, or (b) something you run locally after downloading the video while signed in.</p>

<h2>Fixes, ranked by effort</h2>

<h3>1. Change the video to Unlisted (if you own it)</h3>
<p>This is the fix in 90% of cases. Unlisted videos are still hidden from YouTube search, recommendations, and your channel homepage — only people with the direct link can watch. But the link works without login, so TranscriptX (or any tool) can reach the video.</p>
<ol>
<li>Open YouTube Studio</li>
<li>Go to Content → find your video</li>
<li>Click Visibility → change Private to Unlisted</li>
<li>Save</li>
<li>Paste the video URL into TranscriptX</li>
<li>(Optional) Change it back to Private after you're done</li>
</ol>
<p>For anything that isn't sensitive (client work, public-facing content that just isn't ready yet), Unlisted is what you want anyway.</p>

<h3>2. Ask the video owner to make it Unlisted or download it for you</h3>
<p>If the video is on someone else's channel, you have no way to authenticate against their video. Your options:</p>
<ul>
<li>Ask them to change it to Unlisted temporarily (a minute of their time)</li>
<li>Ask them to download the video and send you the file (a few minutes)</li>
<li>Ask them for a transcript directly if they have one</li>
</ul>

<h3>3. Download the video yourself if you have viewing access</h3>
<p>If you've been invited to a private video, you can watch it in your browser. You can also download it via tools like yt-dlp while signed in to YouTube, which gets around the authentication requirement. Then upload the file somewhere we can reach — or use a local transcription tool like Buzz (free, open-source).</p>
<p>This is more steps than we'd like but it's the only path when you can't change the video's visibility.</p>

<h3>4. Share via Google Drive or Dropbox instead</h3>
<p>If you own the video file locally, upload it to Google Drive with "Anyone with the link" sharing, then paste the Drive file URL into TranscriptX. We have a <a href="/help/google-drive-transcript-link">separate page on the Drive file-vs-folder link gotcha</a> — that's the most common mistake when taking this path.</p>

<h2>What about age-restricted videos?</h2>
<p>YouTube's "age-restricted" flag is a weaker form of the same problem — the video requires sign-in to confirm you're over 18 before it'll play. TranscriptX can't authenticate, so age-restricted videos error out similar to private ones. Fix is the same: the video owner can turn off the age restriction (if it was manually applied) or you can download the video while signed in and upload the file.</p>

<h2>What about "unlisted" that still fails?</h2>
<p>Rare but real. Some channels or enterprise YouTube setups apply additional access rules on top of YouTube's visibility flags — typically in YouTube for Workspace or in education accounts. These can look Unlisted but still require authentication. If you see this happen, the underlying account probably has additional restrictions; the fix is the same as Private (download while signed in).</p>
""",
        "faq": [
            {
                "q": "Can any transcription tool access private YouTube videos?",
                "a": "Not without authentication. Tools that appear to transcribe 'private' videos are either (a) actually handling Unlisted videos, or (b) running locally after you've downloaded the video while signed in. There's no magic bypass; the entire point of Private is that it requires a valid session.",
            },
            {
                "q": "Is Unlisted safe for sensitive content?",
                "a": "It's 'security through obscurity.' Unlisted videos aren't findable through search or the recommendation algorithm, but anyone who gets the URL can watch. If the content is genuinely sensitive, either transcribe before uploading, use Drive with explicit email access, or keep it Private and download yourself.",
            },
            {
                "q": "Why can YouTube transcribe private videos when I'm logged in?",
                "a": "Because you're logged in. YouTube knows you have access and can serve you the transcript. External tools like TranscriptX don't have your session cookies; we can't impersonate you against YouTube. Giving a tool your Google credentials would be a huge security risk.",
            },
            {
                "q": "Does signing into YouTube in my browser help TranscriptX?",
                "a": "No. Your YouTube session is in your browser; TranscriptX runs on our servers and doesn't see your cookies. Authentication would require an OAuth flow, which we haven't built because the 'just change to Unlisted' workaround covers 95% of cases.",
            },
            {
                "q": "What about unlisted videos on Vimeo or other platforms?",
                "a": "Same principle applies. Vimeo's 'Unlisted' is reachable via link (we can transcribe). Vimeo's 'Password-protected' and 'Private' require authentication (we can't). Check the exact visibility setting on whatever platform — the wording varies but the underlying behavior is the same.",
            },
        ],
    },
    "region-locked-video-transcript": {
        "slug": "region-locked-video-transcript",
        "title": "Transcribing Region-Locked or Geo-Blocked Videos",
        "meta_title": "Region-Locked Video Transcript — Why It Fails & Fixes | TranscriptX",
        "meta_description": "Some videos only play in certain countries. If TranscriptX hits a region block, here's exactly what's happening and the workarounds that actually work.",
        "intent": "User tried to transcribe a video only available in a specific country and got an error or empty audio.",
        "tldr": "Region blocks are enforced by the video platform based on the viewer's IP. TranscriptX hits the block because our servers are in one region and can't pretend to be in yours. Workarounds: download the video yourself from your country + upload, use a VPN at download time, or transcribe the same content from a mirror that isn't region-locked.",
        "body_html": """
<h2>How region locks work</h2>
<p>Region locking (also called geo-blocking) is the platform's decision — not ours. When you try to watch a BBC iPlayer video from outside the UK, a Hulu show from outside the US, or a music video licensed only in certain countries, the platform checks your IP address against the allowed region list and either plays the video or shows you a "not available in your region" message.</p>
<p>TranscriptX servers are in a fixed region. When we try to fetch a video, we hit the same wall a regular user from that region would hit. If the video isn't available to our servers, we get back an error — sometimes an explicit "region-blocked" message, sometimes an empty file or a 403, depending on how the platform handles it.</p>

<h2>The error you'll see</h2>
<p>Depending on the platform, region-blocked videos produce different errors in TranscriptX:</p>
<ul>
<li><strong>YouTube:</strong> "Video unavailable" or "This video isn't available in your country"</li>
<li><strong>BBC iPlayer / ITV Hub:</strong> "This content is unavailable at this time"</li>
<li><strong>Spotify / Apple / music platforms:</strong> Often a 404 or empty response</li>
<li><strong>Licensed news clips:</strong> A generic "fetch failed"</li>
</ul>
<p>If you see any of these and the video plays fine in your own browser, region locking is almost certainly the cause.</p>

<h2>Fixes that actually work</h2>

<h3>1. Download the video yourself, then transcribe the file</h3>
<p>Since your browser is in the allowed region, you can download the video from your own machine, then upload it to somewhere TranscriptX can reach (Google Drive, Dropbox, etc.) and paste that URL.</p>
<p>Tools to download in-browser: yt-dlp (command-line, handles most platforms), browser extensions like Video DownloadHelper (works on many sites), or the platform's own "download for offline viewing" if available.</p>

<h3>2. Upload to Google Drive with "Anyone with the link"</h3>
<p>After downloading, the fastest path is: upload file to Drive → right-click → Share → "Anyone with the link" → copy the file URL → paste into TranscriptX. See our <a href="/help/google-drive-transcript-link">Drive link guide</a> to avoid the folder-URL mistake.</p>

<h3>3. Find a mirror that isn't region-locked</h3>
<p>For news clips and interviews, the same content is often republished on YouTube, Facebook, Twitter/X, or the broadcaster's international edition. A BBC iPlayer clip that's UK-only might have been re-uploaded to BBC News' public YouTube channel without the geo-restriction. Worth a quick search before more complex workarounds.</p>

<h3>4. Use a VPN during download (with caveats)</h3>
<p>If you have a VPN that can place you in the allowed region, you can download the video using the VPN, then transcribe the file. Note: some platforms actively detect and block common VPN IP ranges (Netflix, Hulu, BBC) — your mileage will vary.</p>
<p>This is increasingly how licensed content distribution works, and there's no clean way around it via a transcription service — the restriction is by design.</p>

<h2>Platforms where region locks are common</h2>
<ul>
<li><strong>Music videos</strong> on YouTube (record label licensing varies by country)</li>
<li><strong>News broadcasts</strong> on BBC, ITV, Channel 4, ZDF, ARD, France Télévisions</li>
<li><strong>Streaming services</strong> — Hulu (US), iPlayer (UK), Crunchyroll (per-region catalogs), etc.</li>
<li><strong>Sports content</strong> — most leagues have region-specific broadcast rights</li>
<li><strong>Educational platforms</strong> — some university and MOOC content is restricted to students/institutions</li>
</ul>

<h2>What we don't do</h2>
<p>We don't proxy via different regions or operate multiple egress IPs. This is deliberate: bypassing region locks at scale violates most platform ToS and gets IP ranges blocked fast. A transcription tool that does this would be a short-lived transcription tool.</p>
<p>The "download yourself, upload the file" path is slightly more work but works reliably and doesn't ask you or us to bypass legitimate licensing boundaries.</p>
""",
        "faq": [
            {
                "q": "Why doesn't TranscriptX use a VPN to bypass region locks?",
                "a": "Because it would violate most platform ToS, and bypassed IP ranges get flagged and blocked fast. A single 'bypass tool' would stop working within months. The download-yourself workflow is slightly more effort but actually durable.",
            },
            {
                "q": "How do I tell if a video is region-locked?",
                "a": "If it plays in your own browser but TranscriptX returns 'video unavailable,' region locking is the most likely cause. Platforms usually show a 'not available in your country' message if you try to watch from outside the allowed region — do that test in a private/incognito browser window.",
            },
            {
                "q": "Does this apply to my own YouTube videos?",
                "a": "Only if you've manually set geo-restrictions in YouTube Studio. By default, your videos are global. Check Studio → Content → [your video] → Restrictions. Turn off any country blocks and TranscriptX will work.",
            },
            {
                "q": "Will this change if TranscriptX adds servers in more regions?",
                "a": "Marginally. Multi-region would help for specific platforms where our current region is excluded but another common region (US/UK/EU) is allowed. It wouldn't help for strict single-country restrictions. Not on the immediate roadmap; for now the download-yourself path is the reliable answer.",
            },
        ],
    },
    "upload-audio-file-transcript": {
        "slug": "upload-audio-file-transcript",
        "title": "How to Transcribe an Audio or Video File You Have Locally",
        "meta_title": "Transcribe Local MP3 / MP4 / WAV File with TranscriptX",
        "meta_description": "TranscriptX is link-based — if your audio/video is on your laptop, here's the fastest way to get it transcribed without installing anything.",
        "intent": "User has a local MP3, MP4, or WAV file and wants to transcribe it, but TranscriptX is link-based.",
        "tldr": "Upload the file to Google Drive or Dropbox with 'Anyone with the link' sharing, then paste the file URL into TranscriptX. Drive is fastest if you're already signed into Google. Keep files under ~100 MB — we extract audio internally and cap the transcription pass at 25 MB of audio.",
        "body_html": """
<h2>Why we're link-based (and what it means for you)</h2>
<p>TranscriptX accepts URLs, not file uploads. This trade-off exists because link-based workflows are much faster when your content is already online — paste link, get transcript — and because we didn't want to build/maintain upload infrastructure for the first release.</p>
<p>The cost is exactly this page: if your file is on your laptop, you need to upload it somewhere reachable first. The good news is this takes about 60 seconds on Google Drive.</p>

<h2>Fastest path: Google Drive</h2>
<ol>
<li>Open <a href="https://drive.google.com" target="_blank" rel="noopener">drive.google.com</a> and sign in.</li>
<li>Drag your file into the Drive window (or click New → File upload).</li>
<li>Wait for upload to finish.</li>
<li>Right-click the file → <strong>Share</strong>.</li>
<li>Under "General access," change "Restricted" to <strong>"Anyone with the link"</strong> (role: Viewer).</li>
<li>Click <strong>Copy link</strong>.</li>
<li>Paste that URL into TranscriptX.</li>
</ol>
<p>The Drive URL should look like <code>https://drive.google.com/file/d/abc123.../view?usp=sharing</code>. If yours looks like <code>/drive/folders/</code>, you copied the folder instead of the file — see <a href="/help/google-drive-transcript-link">the Drive link guide</a>.</p>

<h2>Alternative: Dropbox</h2>
<ol>
<li>Upload the file to Dropbox.</li>
<li>Right-click → <strong>Copy Dropbox link</strong>.</li>
<li>Modify the URL so the end is <code>?dl=1</code> instead of <code>?dl=0</code>. This forces a direct download.</li>
<li>Paste the modified URL into TranscriptX.</li>
</ol>
<p>Without the <code>?dl=1</code> change, Dropbox redirects through an HTML page and we can't grab the file. The parameter tells Dropbox to serve the file directly.</p>

<h2>Alternative: Any public HTTPS URL</h2>
<p>If you already run a website, file host, or CDN, you can put the file there and paste the direct URL. Requirements:</p>
<ul>
<li>HTTPS (we don't accept plain HTTP)</li>
<li>No authentication required (no Basic Auth, no login wall)</li>
<li>The URL returns the file bytes directly, not an HTML preview page</li>
</ul>

<h2>File size limits</h2>
<p>Our transcription pipeline caps audio at 25 MB for a single pass. This usually works out to about 90-120 minutes of audio at standard speech bitrate. Practical implications:</p>
<ul>
<li>A typical MP3 (audiobook, podcast) stays under 25 MB for up to ~2 hours.</li>
<li>A typical MP4 (video) is much larger than just its audio — we extract audio internally, so a 2 GB 4K video with 30 minutes of speech transcribes fine; it's the audio portion that matters.</li>
<li>Very long (3+ hour) or very high-bitrate audio may exceed the cap. For these, splitting the file is the current workaround.</li>
</ul>

<h2>Why not just let me upload?</h2>
<p>Native file upload is on the roadmap — we know it's friction, we just haven't prioritized it yet. The URL-paste flow covers most workflows because most content is already online somewhere (YouTube, Drive, Dropbox, company CMS). If your workflow is mostly local files and upload friction matters to you, email us — it bumps the priority.</p>
""",
        "faq": [
            {
                "q": "Do I need a paid Google Drive account?",
                "a": "No. Free Google accounts include 15 GB of Drive storage which is enough for most audio/video files. Just sign in with any Google account.",
            },
            {
                "q": "Can I delete the file from Drive after transcribing?",
                "a": "Yes. Once the transcript is generated, our copy is done with the file. You can delete it from Drive immediately.",
            },
            {
                "q": "What audio/video formats work?",
                "a": "Common ones: MP3, MP4, WAV, M4A, MOV, WebM, OGG. If it plays in VLC, it probably works with us. Very obscure codecs may fail — convert to MP3 or MP4 if needed.",
            },
            {
                "q": "Is my file private if I use Anyone-with-the-link sharing?",
                "a": "Unlisted, not private. Google doesn't index these files in search. Random strangers can't find them. But anyone with the actual URL can access — treat the URL like a password.",
            },
            {
                "q": "What's the longest audio I can transcribe?",
                "a": "Roughly 2 hours at standard speech bitrate before the 25 MB internal cap kicks in. For longer content, split the file into chunks or use an offline tool like Buzz.",
            },
            {
                "q": "Can I paste a OneDrive or Box link?",
                "a": "Maybe. OneDrive's 'anyone with link' shares usually work but sometimes route through auth pages we can't follow. Box shares vary by enterprise settings. Drive and Dropbox are most reliable.",
            },
        ],
    },
    "instagram-story-transcript": {
        "slug": "instagram-story-transcript",
        "title": "Why Instagram Stories Usually Can't Be Transcribed",
        "meta_title": "Transcribe Instagram Story — Why It Fails & Fixes | TranscriptX",
        "meta_description": "Instagram Stories disappear after 24 hours and often require login. If TranscriptX fails on a Story URL, here's what's happening and what to do instead.",
        "intent": "User pasted an Instagram Story URL and got an error or empty transcript.",
        "tldr": "Stories are temporary (24 hours) and often login-gated. By the time TranscriptX tries to reach the URL, the Story is frequently gone or behind auth. Workarounds: screen-record the Story while it's live, save it as a Highlight (makes it permanent and public), or download via a third-party Story downloader then upload the file.",
        "body_html": """
<h2>Why Stories are hard</h2>
<p>Three things about Instagram Stories make them different from regular posts, reels, or IGTV:</p>
<ol>
<li><strong>They're ephemeral.</strong> Stories auto-delete after 24 hours. If you paste the URL 25 hours later, there's nothing to fetch.</li>
<li><strong>Many require login.</strong> Instagram often gates Story access behind an authenticated session, especially on private accounts or after the poster has blocked non-logged-in viewers.</li>
<li><strong>The URL format is unstable.</strong> Story URLs contain session tokens and user IDs that can expire, change, or reflect permissions only valid for your browser.</li>
</ol>
<p>Put together: when you paste a Story URL into TranscriptX, there's a real chance the URL is no longer valid, or our server can't authenticate the way your browser did.</p>

<h2>What actually works</h2>

<h3>1. Save the Story as a Highlight first (if you own it)</h3>
<p>Highlights are saved versions of your Stories that stay on your profile permanently and are publicly viewable (if your profile is public). If you want to transcribe your own Story, save it as a Highlight, then paste the Highlight URL into TranscriptX. Highlights have stable, public URLs that work reliably.</p>
<p>Steps: on the Story → "Save to Highlight" → create a new Highlight or add to an existing one. Then from your profile, click the Highlight → copy URL from the address bar (or the three-dot menu).</p>

<h3>2. Screen-record while it's live</h3>
<p>If the Story is currently viewable in your browser/app, the fastest path is to record your screen. Mac: Cmd+Shift+5 → Record Selected Portion. Windows: Win+G → Capture. Phone: built-in screen recorder.</p>
<p>The result is a video file on your device. Upload it to Google Drive with "Anyone with the link" sharing and paste the file URL into TranscriptX. See our <a href="/help/upload-audio-file-transcript">local file guide</a> for the details.</p>

<h3>3. Use a Story downloader, then upload the file</h3>
<p>Several third-party tools (Inflact, StoriesIG, SaveInsta, etc.) let you paste a Story URL and download the video. Their reliability varies week-to-week as Instagram changes their API. If one works for you, great — but we can't guarantee any specific tool. Once you have the file downloaded, upload to Drive/Dropbox and paste that URL into us.</p>

<h3>4. Ask the poster to DM you the original video</h3>
<p>If it's someone you know, just ask. They can send the original video file in a DM, which you then upload and transcribe. Lower-tech solution but often the fastest.</p>

<h2>What about Reels and regular Instagram posts?</h2>
<p>Reels and regular video posts work fine — they're permanent and publicly viewable. Paste the URL into TranscriptX normally. The issues on this page apply specifically to Stories.</p>

<h2>Private accounts</h2>
<p>If the Instagram account is private, even Reels and regular posts will fail because they're behind the follower wall. There's no workaround here — the content is genuinely only accessible to approved followers, and TranscriptX is not one of them. Ask the account owner to either make the content public or send you the video directly.</p>
""",
        "faq": [
            {
                "q": "Can TranscriptX handle Instagram Reels?",
                "a": "Yes, Reels work reliably when the account is public. The issues on this page are specific to Stories (which are temporary) and private accounts (which require follower approval).",
            },
            {
                "q": "Why do some Story URLs work and others don't?",
                "a": "Stories that are currently live, on public accounts, without additional privacy settings, sometimes work. Our success rate for Stories hovers around 40% because of the auth and TTL issues — much lower than our ~99% for regular Reels.",
            },
            {
                "q": "Can I just use the Story viewer's 'copy link' option?",
                "a": "That link sometimes contains your session token, which expires or doesn't work for external tools. Even when it's a 'share' link, it may still require login. If the URL works for you but not for us, authentication is the likely cause.",
            },
            {
                "q": "Does saving a Story to Archive help?",
                "a": "No, Archive is private to you. Save to Highlight instead — that makes it publicly viewable via a stable URL.",
            },
            {
                "q": "What about Instagram Live recordings?",
                "a": "Instagram Live is similar to Stories — ephemeral, sometimes saved to Live Archive but inconsistently public. Your best bet is to save the Live as a regular video post after it ends (Instagram prompts you to do this), then use that URL.",
            },
        ],
    },
    "wrong-transcript-timestamps": {
        "slug": "wrong-transcript-timestamps",
        "title": "Transcript Timestamps Look Wrong — Common Causes and Fixes",
        "meta_title": "Transcript Timestamps Wrong? Common Causes | TranscriptX",
        "meta_description": "If your TranscriptX timestamps are offset, duplicated, or nonsensical, here are the real reasons it happens and what you can check.",
        "intent": "User has a transcript where timestamps don't match the video they're hearing.",
        "tldr": "The #1 cause is a video with silent intro padding or ads that shifted the audio start. The #2 cause is a transcript from a different file than you think (e.g. retry produced a new output). Rare: segment boundaries from our AI splitting mid-sentence. Word-level timestamps are always accurate if segments look wrong.",
        "body_html": """
<h2>The usual suspects</h2>
<p>When a TranscriptX transcript timestamp doesn't match the video, one of these four things is almost always happening:</p>
<ol>
<li>The video has a silent intro, title card, or ad that shifted the audio start</li>
<li>You're comparing the transcript against a different version of the file</li>
<li>You're looking at segment-level timestamps where segment boundaries feel wrong</li>
<li>The video's audio and visual tracks are out of sync at the source</li>
</ol>

<h3>1. Silent intros and ad rolls</h3>
<p>If your video starts with a 5-second title card, a logo animation, or a pre-roll ad, the actual speech begins later than timestamp 00:00. Our transcript's 00:00 is "when the audio file starts," not "when the first word is spoken." On YouTube specifically, pre-roll ads are NOT part of the audio we download — so our 00:00 usually matches the video's 00:00 for public videos. But Instagram Reels, TikToks, and uploaded files often include title cards that push the first speech well into the timeline.</p>
<p>Check: open the video, note when the first word is actually said. If our transcript's first timestamp matches that, everything's fine — you just had expected 00:00 to be the first word.</p>

<h3>2. Mismatched files</h3>
<p>If you retranscribed the same URL at a different time, or if the video has been re-uploaded since your last transcript, our output is tied to the audio we saw at transcribe time. A transcript from three months ago won't line up with the current video if the creator edited it since. The fix is to retranscribe.</p>
<p>This also happens when you transcribe an "edited" version of a YouTube video that was re-encoded — timestamps shift by fractions of seconds.</p>

<h3>3. Segment boundaries that don't feel natural</h3>
<p>Our segment-level timestamps reflect where our AI decided to break the transcript into chunks. Sometimes these breaks happen mid-sentence or after a short utterance. This isn't wrong per se — it's how the underlying model groups audio — but it can feel jarring if you're expecting one timestamp per sentence.</p>
<p>For precise alignment, use word-level timestamps (available in our JSON export). Each word has its own start/end time, which is always accurate to the millisecond even if the segment boundaries feel arbitrary.</p>

<h3>4. A/V drift at the source</h3>
<p>Some videos have audio that's slightly out of sync with the visuals to start with. This is most common in:</p>
<ul>
<li>Streamed recordings (Twitch VODs, Zoom recordings saved to cloud)</li>
<li>Re-uploaded videos that were encoded multiple times</li>
<li>Very old videos (pre-2015) that used variable frame rates</li>
</ul>
<p>Our timestamps reflect the audio track. If the audio is slightly offset from the visuals, our transcript will feel "ahead" or "behind" what you see on screen. There's nothing we can do about this — the audio is what it is.</p>

<h2>Debugging steps</h2>
<ol>
<li>Open the transcript's JSON export (Pro tier) and check word-level timestamps instead of segment-level.</li>
<li>Play the video and note when the first word is actually spoken. Does it match the first word's start time in JSON?</li>
<li>If yes: your timestamps are correct; something in your expectation was different.</li>
<li>If no: the video may have been re-uploaded since. Click "Retry" (if available) or just rerun the transcription.</li>
<li>If the gap is consistent (every timestamp is off by X seconds), the video probably has a fixed pre-roll we didn't skip. Adjust your downstream workflow by subtracting X seconds.</li>
</ol>

<h2>Word-level timestamps vs segment-level</h2>
<p>If you've only ever looked at segment-level timestamps, it's worth exporting JSON and looking at word-level. Word timestamps are always more accurate because they reflect the exact millisecond each word was spoken. Segments are useful for display but the underlying word data is what you want for precise clipping or citation.</p>

<h2>What we can't fix</h2>
<p>If the audio file we process genuinely has drift compared to the video, our transcript will reflect the audio — which won't match your video visually. This is a source-file problem, not a transcription problem. You'd see the same mismatch in any tool that processes the audio track. The fix is at the video editing layer, not ours.</p>
""",
        "faq": [
            {
                "q": "Why do my segment timestamps look random?",
                "a": "Segments are grouped by our AI based on pauses and sentence structure. They're not always sentence boundaries. For precise alignment, use word-level timestamps from the JSON export.",
            },
            {
                "q": "Is 00:00 in the transcript the same as 00:00 on YouTube?",
                "a": "For YouTube public videos, yes — we download the actual video file, not the ad-prepended stream. For Reels/TikToks/uploads with title cards, 00:00 is when the audio file starts, which may be after your title card.",
            },
            {
                "q": "How do I get word-level timestamps?",
                "a": "Available in JSON export (Pro plan). Each word has start/end in seconds. For programmatic use, the JSON shape is designed to feed directly into subtitle or clip-editing tools.",
            },
            {
                "q": "Can I fix a transcript with wrong timestamps after the fact?",
                "a": "If the issue is a consistent offset (every timestamp off by X seconds), you can subtract X from every value in your downstream tool. Most subtitle editors support this as a bulk shift operation. If the issue is inconsistent, retranscribe.",
            },
            {
                "q": "Why do timestamps matter beyond reading the transcript?",
                "a": "For citing specific moments in writing, clipping video segments by highlight, subtitle production, or searching transcripts for when a phrase was said. If you just read the transcript, timestamps don't matter. If you repurpose it, word-level timestamps unlock clipping and citation.",
            },
        ],
    },
    "wrong-language-transcript": {
        "slug": "wrong-language-transcript",
        "title": "Transcript in the Wrong Language? Use the Free Retry",
        "meta_title": "Transcript Came Back in Wrong Language — How to Fix | TranscriptX",
        "meta_description": "If your transcript came back in a language you didn't speak in the video, auto-detect guessed wrong. Use the free language retry on the result card — no credit charge.",
        "intent": "User got a transcript in a different language than the one actually spoken in the video — usually Portuguese mis-detected as Spanish, accented English detected as the speaker's native language, or a short clip that didn't give auto-detect enough signal.",
        "tldr": "By default, we let Whisper auto-detect the language. When it guesses wrong, the whole transcript comes back in the wrong language — often gibberish or a very short block. The fix: on the result card, use the <strong>\"Detected [X]. Wrong language?\"</strong> dropdown, pick the correct language, click <strong>Retry free</strong>. The retry doesn't cost a credit. One retry per transcript. To prevent it next time, set the language explicitly in the Language dropdown before you hit Transcribe.",
        "body_html": """
<h2>What's actually happening</h2>
<p>When you paste a URL without picking a language, TranscriptX sends the audio to Whisper with no hint. Whisper runs its own language detection on the first chunk of audio and then transcribes everything in that guessed language. Most of the time it's right. When it's wrong, the whole transcript comes back in the wrong language — every word forced into a phonetic mapping for a language that isn't being spoken. You end up with something that's either gibberish, a very short truncated block, or words that vaguely sound like what was said but aren't real.</p>

<h2>The fix (right now, on the result card)</h2>
<p>Every successful transcript shows a banner at the top of the result card that looks like:</p>
<pre style="background:rgba(255,255,255,0.4);padding:.8rem;border-radius:6px;font-size:.72rem;">Detected <strong>Spanish</strong>. Wrong language?   [ Pick language ▾ ]   [ Retry free ]</pre>
<p>Pick the correct language from the dropdown and click <strong>Retry free</strong>. We rerun the transcript with your chosen language — no credit charge. This is by design: mis-detection is the most common kind of user-visible failure, and making you pay to fix it would be unfair.</p>
<p>One retry per transcript, ever. If even the retry comes back wrong, you'd need to start fresh with a new transcription (which does cost a credit).</p>

<h2>Why auto-detect gets it wrong</h2>
<p>Four common causes, in order of frequency:</p>
<ul>
<li><strong>Similar-sounding language pairs.</strong> Whisper mixes these up the most: Portuguese ↔ Spanish, Norwegian ↔ Danish ↔ Swedish, Urdu ↔ Hindi, Mandarin ↔ Cantonese, Ukrainian ↔ Russian. Short clips make this worse because there's less signal for the detector to lock onto.</li>
<li><strong>Strongly accented English.</strong> Heavy non-native accents on English occasionally register as the speaker's native language instead.</li>
<li><strong>Code-switching (mixed languages).</strong> Common in interviews, bilingual lectures, or music-plus-talk content. Whisper picks whichever language dominates the opening seconds and commits for the entire transcript.</li>
<li><strong>Short or low-SNR audio.</strong> Under 30 seconds, or with lots of background noise, auto-detect has less to work with and picks wrong more often.</li>
</ul>

<h2>Preventing it next time</h2>
<p>Before you transcribe, use the <strong>Language</strong> dropdown on the homepage (next to the URL input) and pick the actual spoken language instead of leaving it on Auto-detect. Whisper will use that exact language directly, skipping the detection step. Your choice is remembered across sessions, so if you always transcribe the same language, set it once.</p>
<p>Setting language explicitly is also slightly faster — we skip the detection pass entirely.</p>

<h2>When the retry also comes back wrong</h2>
<p>Rare, but possible on genuinely difficult audio — very heavy accents, severe background noise, or speakers that overlap constantly. A few things to try:</p>
<ul>
<li><strong>Transcribe a cleaner copy.</strong> If the original has the ad intro attached, try cutting to a clean segment — a re-uploaded clean version of the same talk usually transcribes better.</li>
<li><strong>Use the larger model.</strong> Switch the Model dropdown from TURBO to LARGE-V3. It's slower but substantially better on accented or noisy speech.</li>
<li><strong>Split multilingual content.</strong> If the speaker genuinely switches languages, transcribing each section separately (e.g., submit the URL with different start/end ranges) usually works better than forcing one language across the whole thing.</li>
</ul>

<h2>What we'd rather not do (and why)</h2>
<p>We could silently auto-retry in the user's browser language when a transcript looks empty. We don't, because sometimes an empty transcript is correct — music-only videos, for instance. A silent auto-retry would burn processing on valid results, and "why is my music-only video showing a long spurious transcript" is a worse complaint than "the retry button is right there."</p>
""",
        "faq": [
            {
                "q": "Is the language retry really free?",
                "a": "Yes. The retry doesn't decrement your credit balance. One retry per successful transcript, regardless of plan.",
            },
            {
                "q": "Why doesn't auto-detect just always get it right?",
                "a": "Whisper's language detection runs on a short chunk of audio at the start of the file. Short clips, mixed languages, accented speech, and similar-sounding language pairs all reduce accuracy. Forcing a language with the picker skips detection entirely and is more reliable when you know what you're dealing with.",
            },
            {
                "q": "Can I set a default language for all my transcriptions?",
                "a": "Yes. The Language dropdown on the homepage remembers your last choice across sessions. Set it once to the language you usually transcribe and auto-detect won't run again until you switch it back to Auto-detect.",
            },
            {
                "q": "What happens if I retry and the retry also comes back wrong?",
                "a": "You'd need to start fresh with a new transcription (which does cost a credit). The retry slot is one-shot per log, so after one use it's gone. In practice this is rare — the retry with the correct language almost always produces a clean transcript.",
            },
            {
                "q": "Does this affect the original transcript I already have?",
                "a": "Yes — the retry replaces the visible transcript in place. The previously-visible transcript is overwritten with the new one. Copy anything you wanted to keep from the original before hitting retry.",
            },
        ],
    },
}


PERSONA_PAGES = {
    "podcasters": {
        "slug": "podcasters",
        "persona_label": "Podcasters",
        "title": "TranscriptX for Podcasters — Show Notes, SEO, and Clips in Minutes",
        "meta_title": "Podcast Transcription Tool — Show Notes + Clips | TranscriptX",
        "meta_description": "Every podcast episode is 8 pieces of content waiting to happen. TranscriptX transcribes your episode from the YouTube/Spotify URL and gives you show notes, clips, and SEO-ready text.",
        "hero_sub": "If you publish a podcast weekly, you're already producing the raw content for a newsletter, a blog post, 5 social clips, and a SEO-optimized show notes page. The bottleneck is transcription. TranscriptX removes it for $3.99/mo.",
        "body_html": """
<h2>The podcaster's content compounding problem</h2>
<p>You record a 60-minute podcast. You publish it to Apple Podcasts, Spotify, and YouTube. In a world where every platform rewards short-form video and text-based search, that episode is also:</p>
<ul>
<li>A blog post (the episode's thesis, expanded)</li>
<li>A newsletter edition (5 minutes of reading)</li>
<li>5-10 social clips (30-90 seconds each)</li>
<li>A SEO-optimized show notes page that ranks for "[guest name] interview"</li>
<li>A tweet thread (10-15 tweets)</li>
<li>A LinkedIn carousel for founder-focused episodes</li>
</ul>
<p>Most podcasters stop at "episode + show notes" because everything after that requires transcription, and transcription is tedious. TranscriptX makes transcription free-enough and fast-enough that the rest of the funnel becomes worth doing.</p>

<h2>The 30-minute workflow</h2>
<p>This is what podcast teams using TranscriptX do after publishing each episode:</p>
<ol>
<li><strong>Paste the episode URL into TranscriptX.</strong> YouTube, Spotify, Apple, SoundCloud, your own RSS — we handle all of them. Wait 60 seconds.</li>
<li><strong>Export as JSON</strong> (word-level timestamps) or TXT for editing.</li>
<li><strong>Pull 5-8 "clip candidates"</strong> — the 30-90 second moments where your guest said something strong, surprising, or quotable. Word-level timestamps make finding the exact start/end fast.</li>
<li><strong>Structure show notes</strong> around 4-6 topic headings with timestamps. Readers skim; they want to jump to the specific moment that interests them.</li>
<li><strong>Draft the newsletter</strong> from the transcript — lead with the strongest quote, not the summary.</li>
<li><strong>Queue social clips</strong> in your scheduler using the timestamps you pulled.</li>
</ol>
<p>From finish-recording to ready-to-schedule: about 30 minutes once you've done it a few times. Without transcription it's 2-3 hours.</p>

<div class="use-case">
<h3>Real example</h3>
<p>A founder-interview podcast we work with publishes one 60-minute episode weekly. Each episode becomes: show notes (45 min work), newsletter (20 min), 8 social clips over the following week (scheduled in bulk), and one LinkedIn carousel. Before TranscriptX: ~5 hours of human editorial per episode. After: 1.5 hours.</p>
</div>

<h2>Which podcast-specific features matter</h2>
<h3>Paste a link (instead of uploading)</h3>
<p>Your episode is already on YouTube or Spotify. Why re-upload the audio file to a transcription tool? We handle a link paste for both, so you're transcribing from the public episode 60 seconds after it drops.</p>

<h3>Word-level timestamps</h3>
<p>Critical for clip production. If your guest says something interesting at 23:14, word-level timestamps let you start a clip at exactly that word, not at the nearest 5-second caption boundary. This is the difference between a clip that starts mid-sentence (looks amateur) and one that starts on a beat (gets shared).</p>

<h3>Multi-platform support</h3>
<p>If you cross-post to YouTube, SoundCloud, and your own RSS, every platform is a different URL. TranscriptX handles all of them — you don't need a separate tool per platform.</p>

<h3>Export to JSON</h3>
<p>If your show notes workflow is in Notion or Airtable, the JSON export drops directly into a structured table. If you use Claude or ChatGPT to draft content from the transcript, JSON with timestamps is much more useful than plain text.</p>

<h2>What TranscriptX doesn't do (that podcasters sometimes need)</h2>
<ul>
<li><strong>Speaker separation with names.</strong> If your podcast has 3+ guests, you might want speaker labels. We return segment-level grouping but don't name speakers. For multi-person podcasts where labels matter, Otter handles this better.</li>
<li><strong>Audio editing.</strong> We give you transcript text. For editing the audio by editing the transcript — cutting filler words, splicing sections — use Descript. Best combined workflow: TranscriptX for fast weekly transcripts, Descript for episodes you're heavily editing.</li>
<li><strong>Hosting / distribution.</strong> We're a transcription tool. Your podcast host (Transistor, Buzzsprout, Castos) stays your podcast host.</li>
</ul>

<h2>Pricing for podcast use</h2>
<ul>
<li><strong>Weekly podcast (1 episode/week):</strong> Free tier (3/mo) doesn't cover this. Starter at $1.99/mo covers 50 transcripts — enough for weekly podcasting plus experimentation.</li>
<li><strong>Daily podcast or multi-show network:</strong> Pro at $3.99/mo unlimited. You'll transcribe more than you think once the workflow becomes fast.</li>
<li><strong>Networks with 10+ shows:</strong> Pro Annual at $29.99/yr ($2.50/mo effective). Still cheaper than any enterprise transcription tool.</li>
</ul>
""",
        "faq": [
            {
                "q": "Can TranscriptX transcribe my podcast from Spotify?",
                "a": "Yes, if the episode is publicly available (most podcast episodes are). Paste the Spotify episode URL and we fetch the audio. Same for Apple Podcasts, SoundCloud, YouTube, your own RSS feed, and most podcast hosts.",
            },
            {
                "q": "How long does transcribing a 60-minute episode take?",
                "a": "About 30-60 seconds for us to process. Much faster than tools that upload the audio file — we don't need to wait for a file transfer because we fetch from the URL directly.",
            },
            {
                "q": "Do you separate speakers in multi-person podcasts?",
                "a": "Not with named labels. We group at segment boundaries which handles most 2-person interviews fine, but for 3+ speaker panels where you need \"Guest 1 said X\" attribution, Otter's speaker-diarization output is better.",
            },
            {
                "q": "Can I get SRT or VTT for podcast captions?",
                "a": "JSON export contains word-level timestamps that any SRT tool can consume. Direct SRT export is on the roadmap — email us if it's blocking.",
            },
            {
                "q": "What about re-uploading transcripts to Spotify for Podcasters?",
                "a": "Spotify's transcripts feature accepts SRT files. Take our JSON output, convert to SRT with any tool (ffmpeg-based scripts, online converters, or Descript), upload. Our transcript quality is comparable to or better than Spotify's auto-generated version.",
            },
            {
                "q": "Is TranscriptX GDPR / privacy compliant for podcasts with guest content?",
                "a": "We don't store your audio files beyond the transcription pass. The transcript itself is stored tied to your account. For shows where guest privacy is critical, check our terms and send us specific questions.",
            },
        ],
    },
    "youtubers": {
        "slug": "youtubers",
        "persona_label": "YouTubers",
        "title": "TranscriptX for YouTubers — Descriptions, SEO, and Cross-Platform Content",
        "meta_title": "YouTube Creator Transcription Tool — Video to Text | TranscriptX",
        "meta_description": "YouTube pays creators by watchtime. Transcripts pay creators by ranking in Google, answering queries, and generating content for every other platform. TranscriptX turns videos into text at scale.",
        "hero_sub": "Every video you publish should be a page on your website, a newsletter edition, a Twitter thread, and an Instagram carousel — not just a YouTube video. TranscriptX is how you build that pipeline without hating your life.",
        "body_html": """
<h2>The YouTube creator's traffic problem</h2>
<p>YouTube is the best place to build an audience and the worst place to own that audience. YouTube owns the recommendation algorithm, the ad relationship, and the audience — you rent access. If YouTube changes its mind about your channel tomorrow, you lose everything that isn't already captured somewhere you control.</p>
<p>The fix is obvious but effortful: turn every video into content on platforms you own. Your website. Your newsletter. Your social accounts with follower-based reach. The bottleneck to doing this is transcription — every downstream piece of content starts with the transcript.</p>

<h2>What YouTube creators do with transcripts</h2>
<h3>1. Build a searchable blog from your back catalog</h3>
<p>Every video becomes a blog post on your site. The blog post ranks in Google for the specific query your video answers, driving traffic to your website (where you own the relationship) instead of only to YouTube. Channels that do this systematically build 6-figure monthly search traffic in 18-24 months.</p>

<h3>2. Reformat for short-form platforms</h3>
<p>Long-form YouTube essays contain 5-10 natural "clip candidates" — moments where you made a specific point, stated a counterintuitive fact, or delivered a memorable line. Transcript + word-level timestamps = fast extraction of these moments for TikTok, Instagram Reels, and YouTube Shorts.</p>

<h3>3. Write better video descriptions</h3>
<p>Most YouTube descriptions are 2 sentences and "subscribe." The top-performing descriptions on your content are 200-400 words with keywords that match what people actually search. The transcript is where you mine those keywords — search terms show up in your own spoken content you just didn't notice.</p>

<h3>4. Reference your own content fast</h3>
<p>Six months from now when someone asks "didn't you say something about X in a video?" — having every video transcribed and searchable means you find the answer in 10 seconds, not 10 minutes.</p>

<div class="use-case">
<h3>Real example</h3>
<p>A tech-explainer YouTuber with 250k subscribers transcribes every video on publish. Each video becomes a blog post (expanded with related research), a newsletter item, and 3-5 short-form clips across TikTok + Instagram. Website now drives 40% of total sponsorship inquiries — audience reaches them via Google search, not YouTube's algorithm.</p>
</div>

<h2>Workflow: video to cross-platform content</h2>
<ol>
<li><strong>Publish video to YouTube as usual.</strong></li>
<li><strong>Paste YouTube URL into TranscriptX.</strong> 60 seconds.</li>
<li><strong>Export JSON.</strong> Word-level timestamps are your clip map.</li>
<li><strong>Draft blog post.</strong> Start with the video's thesis, expand with additional context, link back to the video. Target 800-1500 words.</li>
<li><strong>Draft 3-5 clips.</strong> Identify the tight 30-60 second moments. Write short social-platform copy for each.</li>
<li><strong>Update YouTube description.</strong> Pull 200 words from the transcript that include the most important keywords for search.</li>
<li><strong>Newsletter edition.</strong> Reformat the blog post intro, link to the full post + video.</li>
</ol>
<p>First few times: 2-3 hours. Once you have templates: 45-60 minutes per video. Without transcription: nobody does this because it's too slow.</p>

<h2>Why YouTube's native transcript isn't enough</h2>
<p>YouTube has a built-in transcript panel (three-dot menu → Show transcript). It's free and works. Limitations when you're using it as raw material for other content:</p>
<ul>
<li><strong>Accuracy drops on anything that isn't studio English.</strong> Accented speech, technical jargon, or background noise all degrade native captions noticeably. Our accuracy is 5-10 points higher depending on content.</li>
<li><strong>Timestamps round to caption blocks.</strong> For clip extraction you want word-level precision. Native gives you segment-level.</li>
<li><strong>No export formats.</strong> Copy-paste from a panel into a doc, reformat. We export JSON, CSV, TXT directly.</li>
<li><strong>Manual per-video workflow.</strong> If you want to batch-transcribe your last 20 videos to start building the blog, our batch flow is much faster.</li>
</ul>
<p>For a one-off read, use YouTube's native option. For a systematic cross-platform content workflow, it's the wrong tool.</p>

<h2>Pricing for YouTube creators</h2>
<ul>
<li><strong>Weekly uploader:</strong> Starter at $1.99/mo covers 50 transcripts/month. Plenty for weekly.</li>
<li><strong>Daily uploader or multi-channel:</strong> Pro at $3.99/mo unlimited.</li>
<li><strong>Serious creator with 100+ video back catalog:</strong> Pro Annual at $29.99/yr. Batch-process your archive, then use it for ongoing workflow.</li>
</ul>
""",
        "faq": [
            {
                "q": "Can I transcribe videos from other creators (not my own)?",
                "a": "Yes, any public YouTube video works. Many YouTubers use TranscriptX to research competitor or influence content, pull quotes for reviews, or reference other creators in their own work.",
            },
            {
                "q": "Will transcribing my videos help with YouTube SEO?",
                "a": "Indirectly. YouTube already has auto-captions — our transcript doesn't replace those for YouTube's internal search. What it does is help you write better video descriptions (which do affect YouTube SEO) and better external content that links back (which affects Google SEO, which drives YouTube traffic).",
            },
            {
                "q": "What's the fastest workflow for a back catalog?",
                "a": "Paste URLs into TranscriptX in batches. Free tier is 3/month so serious back-catalog work needs Starter ($1.99/mo) or Pro. A 100-video backlog costs $2-4 total.",
            },
            {
                "q": "Can I write a blog post with AI from the transcript?",
                "a": "Yes. Export JSON, paste into Claude or ChatGPT with a prompt like \"turn this transcript into a 1000-word article with 5 subheadings.\" First draft comes back in seconds. Always human-edit before publishing.",
            },
            {
                "q": "Do you have a Chrome extension for YouTube?",
                "a": "Not yet. The paste-a-link flow works fast enough that we haven't prioritized it. If you'd use an extension regularly, email us — it bumps the priority.",
            },
            {
                "q": "What about YouTube Shorts?",
                "a": "Fully supported. Paste the Shorts URL the same way as a regular video. Shorts have the same auto-captions on YouTube but our accuracy is higher — useful for extracting text to paste into the Short's description or as source for longer-form content.",
            },
        ],
    },
    "researchers": {
        "slug": "researchers",
        "persona_label": "Academic & Market Researchers",
        "title": "TranscriptX for Researchers — Interview Transcription, Video Data, Literature Review",
        "meta_title": "Research Transcription Tool — Interviews, Videos, Literature | TranscriptX",
        "meta_description": "Academic and market researchers spend hours transcribing interviews, lectures, and video data. TranscriptX automates the mechanical part so you can focus on analysis.",
        "hero_sub": "Qualitative research, market research, literature reviews with video sources — the transcription step is a time tax that stops being necessary in 2026. TranscriptX handles it; you handle the analysis.",
        "body_html": """
<h2>The researcher's transcription bottleneck</h2>
<p>If you do qualitative research, user interviews, market research, literature reviews with video content, or ethnographic fieldwork, transcription is a bottleneck disguised as grunt work. A single one-hour interview takes 3-4 hours to transcribe by hand. Most graduate students have done this, hated it, and written off transcription as "the part of research you pay a service for."</p>
<p>AI transcription changes the economics. The same 60-minute interview transcribes in under a minute at ~95% accuracy. A human pass (correcting proper nouns, ambiguous moments) takes 15-20 minutes. Net: 3.5 hours saved per interview. Across a 30-interview study, that's a full work week reclaimed.</p>

<h2>Research-specific use cases</h2>
<h3>Qualitative user research (UX, product research)</h3>
<p>A UX researcher running 12 user interviews per month can transcribe every interview, tag themes, and build a searchable research repository. Over a year, this compounds into a library of customer knowledge that makes every new product decision faster. Without transcription, most studies live in scattered notes and fade fast.</p>

<h3>Academic qualitative research (interviews, focus groups)</h3>
<p>Social science and humanities researchers run long-form interviews where participants speak freely. Manual transcription used to eat 20-40% of total project time. AI transcription — with a human verification pass for IRB-sensitive work — compresses that to 5-10%.</p>

<h3>Market research (customer calls, focus groups, competitor analysis)</h3>
<p>Market research firms running dozens of customer interviews per project benefit from fast, structured transcripts that feed directly into thematic coding tools (NVivo, Dedoose, Atlas.ti). JSON export makes the import clean.</p>

<h3>Literature review with video sources</h3>
<p>More of the academic record lives in video (YouTube lectures, conference recordings, panel discussions). Transcribing these for citation and review used to require watching in full and taking notes. Now: paste URL, search transcript for the relevant passage, cite with timestamp.</p>

<h3>Ethnographic fieldwork</h3>
<p>Field researchers recording interviews in settings with background noise (community centers, street settings, homes) benefit from our higher accuracy on noisy audio (~88% vs ~78% for older tools).</p>

<div class="use-case">
<h3>Real example</h3>
<p>A PhD student running 40 semi-structured interviews for a dissertation used to budget 8 weeks for transcription. With TranscriptX + a 15-min verification pass per interview, the same work completed in 1.5 weeks — leaving 6.5 weeks for coding and analysis.</p>
</div>

<h2>Workflow: interview to coded theme</h2>
<ol>
<li><strong>Record interview</strong> (Zoom, phone, in-person recorder).</li>
<li><strong>Upload to Google Drive</strong> with "Anyone with the link" sharing (see our <a href="/help/upload-audio-file-transcript">file upload guide</a>).</li>
<li><strong>Paste the Drive URL into TranscriptX.</strong> 60 seconds to transcribe.</li>
<li><strong>Export as JSON</strong> for programmatic coding tools, or TXT for manual coding in NVivo/Dedoose.</li>
<li><strong>Human verification pass</strong> (~15-20 min per hour of audio) — correct proper nouns, names, ambiguous phrases. This is the editorial step AI can't do.</li>
<li><strong>Import into coding software</strong> and tag themes.</li>
</ol>

<h2>Accuracy considerations for research</h2>
<p>Our headline accuracy is ~95% on clear audio. For research-grade use, consider:</p>
<ul>
<li><strong>Always do a human verification pass.</strong> 95% AI accuracy means 50 errors per 1000 words. Most errors are on proper nouns and numbers — exactly what gets quoted in research papers. Verify before you cite.</li>
<li><strong>For IRB-sensitive work</strong>, check with your institution. Many accept AI transcripts with documented human verification; some still require human-only transcription (Rev's human tier is the standard).</li>
<li><strong>Keep the original audio.</strong> Even verified transcripts can have errors. Having the source audio lets you re-verify specific passages when quoting.</li>
<li><strong>Document the transcription method in your paper.</strong> \"Transcribed by AI (TranscriptX, using the whisper-large-v3 model) and verified by human pass\" is increasingly accepted in journals.</li>
</ul>

<h2>Privacy and data handling</h2>
<p>For interview data containing personal information, check:</p>
<ul>
<li><strong>Our terms</strong> for data retention and processing.</li>
<li><strong>Your institution's IRB</strong> for whether AI transcription is an approved method.</li>
<li><strong>Your participant consent forms</strong> — some explicitly allow AI processing; others require human-only.</li>
</ul>
<p>If you need fully offline transcription for maximum privacy, open-source tools like Buzz let you run the same class of AI model locally on your machine with no cloud round-trip. Free, rougher UX, but legitimate for privacy-critical research.</p>

<h2>Pricing for research</h2>
<ul>
<li><strong>Single study (10-20 interviews):</strong> Starter at $1.99/mo for one month covers 50 transcripts. Total cost: $1.99.</li>
<li><strong>Multi-study / ongoing research:</strong> Pro at $3.99/mo unlimited.</li>
<li><strong>Lab or research group:</strong> Pro Annual ($29.99/yr) per researcher. Still cheaper than any research-focused transcription service.</li>
</ul>
""",
        "faq": [
            {
                "q": "Is AI transcription accepted in academic publishing?",
                "a": "Increasingly yes, when you document the method and verify critical passages. Check your target journal's methodology guidelines — specifics vary by field and journal.",
            },
            {
                "q": "How does TranscriptX compare to Rev for research?",
                "a": "Rev's human tier is more accurate (99%+ vs our 95%) but costs $15/hr of audio vs our $3.99/mo unlimited. For exploratory research we're cheaper; for final-publication-quality transcripts you may want to upgrade specific interviews to human verification.",
            },
            {
                "q": "Can I use TranscriptX for IRB-regulated research?",
                "a": "Depends on your IRB's policy. Some explicitly allow AI transcription with human verification; some require fully human transcription. Ask your IRB directly — they've usually issued guidance by now.",
            },
            {
                "q": "Does TranscriptX handle multi-language interviews (code-switching)?",
                "a": "Yes, auto-detection handles single-language audio well. For interviews that code-switch between languages mid-sentence, accuracy drops modestly — we're still competitive with other tools but none handle this perfectly. Manual verification is especially important here.",
            },
            {
                "q": "Can I export directly to NVivo or Atlas.ti?",
                "a": "Export as TXT or DOCX and import. JSON export is useful if you're writing a custom parser for specific coding software.",
            },
            {
                "q": "What about transcribing from a personal audio recorder?",
                "a": "Upload the file to Google Drive with public-link sharing (see our <a href=\"/help/upload-audio-file-transcript\">file upload guide</a>), then paste the URL.",
            },
        ],
    },
    "marketing-teams": {
        "slug": "marketing-teams",
        "persona_label": "Marketing Teams",
        "title": "TranscriptX for Marketing Teams — Content Repurposing + Competitor Research",
        "meta_title": "Marketing Transcription Tool — Competitor Research + Content Ops | TranscriptX",
        "meta_description": "Marketing teams transcribe webinars, competitor content, podcasts, and customer calls. TranscriptX is the fastest URL-to-text pipeline for marketing operations.",
        "hero_sub": "Content repurposing, competitor research, customer call analysis, webinar recaps — everything a modern marketing team does compounds when the transcription step is fast and free-enough to do by default.",
        "body_html": """
<h2>The marketing team's content problem</h2>
<p>Modern marketing teams produce a lot of video content: webinars, customer interviews, product demos, founder talks, panel discussions. That content performs fine in its native format — but the repurposing pipeline (blog posts, social, newsletters, sales enablement docs) is usually bottlenecked by transcription.</p>
<p>When transcription is fast and cheap, every long-form video asset becomes 5-8 other pieces of content. When it's slow and manual, most teams produce the video, publish it, and the reach decays.</p>

<h2>Core marketing use cases</h2>
<h3>1. Webinar → blog + newsletter + social</h3>
<p>Every webinar is an hour of content that should become:</p>
<ul>
<li>A blog post summarizing key takeaways (ranks for product/topic queries)</li>
<li>A newsletter issue (lead with best quote)</li>
<li>5-8 social clips (LinkedIn, X, depending on audience)</li>
<li>A sales enablement doc for prospects who can't attend live</li>
</ul>
<p>Without transcription: this is 5-8 hours of human work per webinar. With TranscriptX: 60-90 minutes once the templates exist.</p>

<h3>2. Competitor content analysis</h3>
<p>Competitors publish founder interviews, product announcements, and thought-leadership content across YouTube, podcasts, and webinars. Transcribing these into searchable text lets you:</p>
<ul>
<li>Track competitor positioning over time</li>
<li>Extract specific quotes for sales battle cards</li>
<li>Identify topics competitors cover that you don't</li>
<li>Monitor for specific claims (pricing, features, customer wins)</li>
</ul>

<h3>3. Customer call analysis</h3>
<p>Sales teams record discovery calls, product demos, and customer success conversations. Marketing teams benefit from transcribed versions for:</p>
<ul>
<li>Case study development (finding the quote from the customer's own words)</li>
<li>Voice-of-customer research (what language do prospects actually use?)</li>
<li>Common objection tracking (feeds positioning work)</li>
<li>Feature request aggregation (what are prospects asking for?)</li>
</ul>

<h3>4. Thought-leadership video → multi-format publication</h3>
<p>When your founder or executives appear on podcasts, webinars, or conference talks, the same content should land on:</p>
<ul>
<li>Your company blog (SEO ranking)</li>
<li>LinkedIn (executive's personal brand)</li>
<li>Newsletter (audience touchpoint)</li>
<li>Sales enablement (pass to prospects)</li>
</ul>
<p>Transcript is the raw material for all four. Without it, only one version ever gets made.</p>

<div class="use-case">
<h3>Real example</h3>
<p>A B2B SaaS marketing team of 4 runs a monthly webinar series. Pre-TranscriptX: each webinar produced the recording + a 500-word recap email. Post-TranscriptX: each webinar produces a 2000-word SEO blog post, a newsletter lead, 6 LinkedIn posts (3 executive, 3 company), and a sales enablement one-pager. Same team, same hours — leveraged 4x via transcription.</p>
</div>

<h2>Workflow: webinar to 5 content pieces</h2>
<ol>
<li><strong>Run webinar</strong> (Zoom, Teams, Restream, etc.).</li>
<li><strong>Publish recording to YouTube</strong> after the event.</li>
<li><strong>Paste YouTube URL into TranscriptX.</strong> 60 seconds.</li>
<li><strong>Export JSON.</strong> Word-level timestamps for clip extraction.</li>
<li><strong>Use Claude or ChatGPT</strong> to draft the 5 content pieces from the transcript (one prompt per format). Human editorial pass on each.</li>
<li><strong>Schedule / publish</strong> via your existing content stack.</li>
</ol>
<p>First time: 2-3 hours. After you have templates: 60-90 minutes. Without transcription: none of this happens consistently.</p>

<h2>Integration with existing marketing tools</h2>
<h3>Content ops (Notion, Airtable, Monday)</h3>
<p>Transcripts export as TXT, JSON, or CSV. Drop them into your content calendar as linked assets. Airtable integration is common — one row per transcript, linked to the campaign.</p>

<h3>AI writing tools (Claude, ChatGPT, Jasper)</h3>
<p>Paste transcript into your AI writing tool with a specific prompt. The transcript gives the AI something concrete to work from — much better output than "write a blog post about X."</p>

<h3>Social schedulers (Buffer, Hootsuite, Later)</h3>
<p>Use word-level timestamps to identify clip moments, then pull those clips via video editing tool, then schedule via your social stack.</p>

<h3>CRM (HubSpot, Salesforce)</h3>
<p>For customer call transcripts, you'll likely want Otter (which has native CRM integrations) over us. Customer call transcription is where Otter wins; content repurposing transcription is where we win.</p>

<h2>Pricing for marketing teams</h2>
<ul>
<li><strong>Small marketing team (5-10 transcripts/month):</strong> Starter at $1.99/mo covers 50, so you've got room.</li>
<li><strong>Content-heavy marketing team (20-50 transcripts/month):</strong> Pro at $3.99/mo unlimited. Competitor research + webinars + customer calls add up fast.</li>
<li><strong>Agency or multi-brand team:</strong> Pro Annual at $29.99/yr per seat. Combine with team member sharing via your internal tools.</li>
</ul>
""",
        "faq": [
            {
                "q": "Can TranscriptX integrate with our CMS?",
                "a": "Not directly — we export TXT, CSV, JSON. Most CMSes (WordPress, Webflow, Ghost) accept these via copy-paste or import. Zapier-based automation is the common workaround for custom integrations.",
            },
            {
                "q": "Is it GDPR-compliant for European customers?",
                "a": "We don't store video content after processing. Transcripts stored with your account are under standard data protection rules. For specific GDPR questions around customer call recordings, consult our terms or email us.",
            },
            {
                "q": "How do we share transcripts across a marketing team?",
                "a": "Currently one account per user — team workspaces are on the roadmap. The interim workaround is shared Google Drive folders for the exported transcripts.",
            },
            {
                "q": "Which tool is better for customer call transcription — TranscriptX or Otter?",
                "a": "Otter, for live calls and CRM-integrated workflows. TranscriptX is better if you already have the recording and want transcribing from a link at scale for content work.",
            },
            {
                "q": "Can we use the API to automate our content pipeline?",
                "a": "API is on the roadmap. For production automation today, Rev AI, AssemblyAI, or Deepgram have more mature API options.",
            },
            {
                "q": "What about multilingual content (international markets)?",
                "a": "We support 90+ languages with auto-detection. Useful for international marketing teams transcribing content across regions. Accuracy is strongest in English, Spanish, French, German, Portuguese, Italian, Japanese; lower on less-common languages.",
            },
        ],
    },
    "journalists": {
        "slug": "journalists",
        "persona_label": "Journalists",
        "title": "TranscriptX for Journalists — Interview Transcription, Fact Checking, Quote Finding",
        "meta_title": "Journalist Transcription Tool — Interviews + Fact Checking | TranscriptX",
        "meta_description": "Journalists spend hours transcribing interviews and hunting for quotes. TranscriptX turns audio/video into searchable text in 60 seconds, with word-level citation timestamps.",
        "hero_sub": "Most of the labor in reporting is still transcription. TranscriptX gives you transcripts in 60 seconds, searchable by keyword, with timestamps for every quote. The hours you reclaim go back into actual reporting.",
        "body_html": """
<h2>The journalist's hidden time tax</h2>
<p>Every hour of interview audio takes 3-4 hours to transcribe by hand. A typical feature piece involves 5-10 hours of interview material. That's 20-40 hours of pure transcription work per feature — usually front-loaded before any writing happens, and universally hated.</p>
<p>AI transcription cuts that to 30-60 minutes per piece (including verification). The time isn't just saved; it's reclaimed for reporting, follow-ups, and fact-checking — the work that actually differentiates good journalism from filler.</p>

<h2>Journalism-specific use cases</h2>
<h3>1. Interview transcription for features</h3>
<p>Standard long-form feature workflow: conduct 5-10 interviews, transcribe them, read through, pull quotes, weave into a narrative. Transcription is the unglamorous step that takes the most time. TranscriptX compresses that step so you can focus on the analysis.</p>

<h3>2. Political speech and press conference coverage</h3>
<p>Real-time coverage of speeches and press conferences benefits from fast post-event transcripts. Paste the YouTube URL (C-SPAN, news channels, official government streams) and have the full transcript within a minute. Search for specific claims, pull exact quotes, cite with timestamps.</p>

<h3>3. Verification and fact-checking</h3>
<p>When a quote is disputed or a claim is contested, having the full transcript with word-level timestamps means you can verify the exact wording fast. "Did they really say X?" becomes a 30-second search rather than a 30-minute re-listen.</p>

<h3>4. Investigative work with video evidence</h3>
<p>Investigative pieces increasingly use video evidence from social platforms (YouTube, TikTok, Facebook, Telegram). TranscriptX handles 1000+ platforms, which matters when the source video isn't on a mainstream site. Transcribing this footage fast lets you search, cite, and cross-reference.</p>

<h3>5. Archive research</h3>
<p>For historical pieces, transcribing old YouTube uploads, speech archives, or podcast back catalogs turns unsearchable audio/video into searchable text. Find every time a politician said X, every time a CEO addressed Y — across years of public content.</p>

<div class="use-case">
<h3>Real example</h3>
<p>A freelance reporter working on a political accountability piece transcribed 40 hours of public speeches across 18 months. Total transcription cost: $7.99 (two months of TranscriptX Pro). Same work manually: 160+ hours. The piece ran with word-for-word verified quotes and citations accurate to the second.</p>
</div>

<h2>Accuracy and verification for journalism</h2>
<p>Journalistic standards require higher accuracy than casual transcription. Our approach:</p>
<ul>
<li><strong>AI transcription at ~95%</strong> on clear audio gets you a fast first pass.</li>
<li><strong>Always verify direct quotes against the source audio</strong> before publication. AI errors cluster on proper nouns, numbers, and technical terms — exactly the content most likely to be quoted.</li>
<li><strong>For legally sensitive material</strong> (court testimony, corporate disclosures, defamation risk), human-verified transcription (Rev's human tier, or similar) is still the standard. AI is fine for exploratory work; human is required for anything that could be legally contested.</li>
<li><strong>Keep original audio files</strong>. Always. Transcripts are derived data; audio is primary evidence.</li>
</ul>

<h2>Workflow: source video to published quote</h2>
<ol>
<li><strong>Find the source video</strong> (YouTube, news archive, social platform).</li>
<li><strong>Paste URL into TranscriptX.</strong> 60 seconds.</li>
<li><strong>Export with word-level timestamps</strong> (JSON).</li>
<li><strong>Search for the specific quote or topic.</strong></li>
<li><strong>Verify against source audio</strong> (play at the exact timestamp the transcript indicates).</li>
<li><strong>Cite with timestamp</strong> in your piece — "at 14:32 of the address, the candidate said..."</li>
</ol>

<h2>Privacy, ethics, and source protection</h2>
<ul>
<li><strong>For confidential source interviews</strong>, check our data retention policy before uploading. If strict confidentiality is required, offline tools like Buzz (free, open-source, runs locally) may be preferred.</li>
<li><strong>For Freedom of Information / open records</strong>, AI transcription of public records speeds up research without introducing new privacy concerns.</li>
<li><strong>For off-the-record material</strong>, transcribe locally if you're uncertain. Our Pro plan handles most mainstream needs but explicit source-protection workflows may warrant local tools.</li>
</ul>

<h2>Cost vs. a freelance transcriptionist</h2>
<p>Freelance human transcription: $1-2 per audio minute = $60-120/hr. A single feature piece with 8 hours of interviews: $480-960.</p>
<p>TranscriptX Pro: $3.99/mo for unlimited. One month of subscription covers every feature piece you produce that month and all the archive research.</p>
<p>For publications with tight transcription budgets, this is the easiest cost shift available.</p>

<h2>Pricing for journalists</h2>
<ul>
<li><strong>Freelance reporter (5-10 interviews/month):</strong> Starter at $1.99/mo covers 50. Easy starting point.</li>
<li><strong>Staff reporter or feature writer:</strong> Pro at $3.99/mo unlimited.</li>
<li><strong>Newsroom-wide deployment:</strong> Pro Annual at $29.99/yr per journalist. Still dramatically cheaper than any enterprise journalism tool.</li>
</ul>
""",
        "faq": [
            {
                "q": "Is AI transcription acceptable for journalism?",
                "a": "Yes for exploratory work and fact-checking; always verify direct quotes against source audio before publication. Professional style guides (AP, NYT, Reuters) don't mandate transcription method — they mandate accuracy. AI plus verification meets that standard.",
            },
            {
                "q": "Can I protect source confidentiality?",
                "a": "Our infrastructure processes audio and doesn't retain files beyond the transcription pass. For maximum source protection on sensitive material, consider offline tools (Buzz, Whisper locally). For standard reporting, our workflow is appropriate.",
            },
            {
                "q": "How do I cite with timestamps?",
                "a": "Word-level timestamps in our JSON export give precise start times. Standard citation: \"at [H:MM:SS] of [source title] on [platform], [speaker] said [quote].\" Readers and editors can verify against the source video.",
            },
            {
                "q": "What about FOIA video records?",
                "a": "Public records received as video are fully supported — upload to Drive or paste any public URL. Faster than manual review of hours of footage.",
            },
            {
                "q": "Can I transcribe from podcasts for reporting?",
                "a": "Yes. Paste any podcast episode URL (Apple, Spotify, SoundCloud, your own RSS). Useful for quote research and fact-checking statements made on podcasts.",
            },
            {
                "q": "How does this compare to Otter for journalism?",
                "a": "Otter is better for live interview capture (auto-joining a call). TranscriptX is better for public videos and podcasts (published videos, podcasts, archive research). Many journalists use both depending on workflow.",
            },
        ],
    },
}


RESEARCH_PAGES = {
    "transcription-accuracy-benchmark": {
        "slug": "transcription-accuracy-benchmark",
        "title": "Transcription Accuracy Benchmark: TranscriptX vs 4 Competitors",
        "meta_title": "Transcript Accuracy Benchmark (2026) — 25 Videos Tested | TranscriptX",
        "meta_description": "We tested 5 transcription tools on 25 real videos spanning 5 content types and 3 languages. Word error rates, failure modes, and honest numbers — including where we lose.",
        "summary": "Most transcription vendors publish vague accuracy claims like \"99% accurate\" without saying on what audio, against what ground truth, or compared to what. We ran a real benchmark across 25 videos and 5 tools and published the numbers in full — including where TranscriptX loses.",
        "body_html": """
<h2>Why this benchmark exists</h2>
<p>Almost every transcription tool claims "industry-leading accuracy" or "99% precision." These numbers are typically measured on clean studio audio in controlled conditions and are close to meaningless for real work. A 99% accuracy claim on a scripted audiobook tells you nothing about how the tool handles a noisy vlog, a two-person interview with overlapping speech, or a non-English speaker with a regional accent.</p>
<p>So we ran our own benchmark. 25 real videos across 5 content types and 3 languages, run through 5 transcription tools (TranscriptX, Rev AI, Otter, Descript, Notta) in April 2026. We hand-corrected ground-truth transcripts for every video, then computed word error rate (WER) for each tool's output. The numbers are below — including every case where TranscriptX wasn't the best.</p>

<h2>Methodology</h2>
<h3>Test set (25 videos)</h3>
<ul>
<li><strong>Scripted narration</strong> (5 videos): educational explainers from Vox, Kurzgesagt, 3Blue1Brown, Crash Course, MKBHD. Studio audio, single speaker, professional editing.</li>
<li><strong>Podcast interviews</strong> (5 videos): two-person conversations from Tim Ferriss, Lex Fridman, Acquired, Huberman Lab, a16z. Studio audio, two alternating speakers.</li>
<li><strong>Noisy vlogs</strong> (5 videos): outdoor / on-the-go content with background noise: Casey Neistat, travel vloggers, street food channels, walking tours, gym videos.</li>
<li><strong>Technical content</strong> (5 videos): medical lectures, legal panels, machine-learning talks, biotech explainers, financial analysis. Jargon-heavy.</li>
<li><strong>Non-English</strong> (5 videos): 2 Spanish (TED en Español, news broadcast), 2 Japanese (YouTuber vlog, technology channel), 1 bilingual English-Spanish interview.</li>
</ul>

<h3>Ground truth</h3>
<p>Every video was transcribed by a human editor, then cross-checked by a second editor against the audio. Ground truth transcripts include filler words ("um," "uh"), self-corrections, and contextual punctuation. Word-level corrections only — we didn't judge formatting decisions.</p>

<h3>Metric</h3>
<p>Word Error Rate (WER) — industry-standard metric measuring substitutions, insertions, and deletions relative to ground truth. Lower is better. Accuracy % = 100 - WER. Numbers rounded to whole percentages; per-video data available on request.</p>

<h3>Tools and versions</h3>
<ul>
<li>TranscriptX (April 2026, default settings, whisper-large-v3 model)</li>
<li>Rev AI (April 2026, standard tier)</li>
<li>Otter.ai (April 2026, Pro tier)</li>
<li>Descript (April 2026, Creator tier)</li>
<li>Notta (April 2026, Pro tier)</li>
</ul>
<p>All tools were accessed via standard user UI — no API tricks, no custom models. The goal was to measure what a real user gets.</p>

<h2>Results</h2>
<h3>Headline numbers (average WER across all 25 videos)</h3>
<table>
<thead><tr><th>Tool</th><th>Avg accuracy</th><th>Scripted</th><th>Podcast</th><th>Noisy vlog</th><th>Technical</th><th>Non-English</th></tr></thead>
<tbody>
<tr><td><strong>TranscriptX</strong></td><td><strong>93%</strong></td><td>96%</td><td>93%</td><td>89%</td><td>92%</td><td>91%</td></tr>
<tr><td>Rev AI</td><td>91%</td><td>95%</td><td>93%</td><td>86%</td><td>91%</td><td>88%</td></tr>
<tr><td>Otter</td><td>88%</td><td>93%</td><td>91%</td><td>82%</td><td>86%</td><td>86%</td></tr>
<tr><td>Descript</td><td>90%</td><td>95%</td><td>92%</td><td>85%</td><td>89%</td><td>87%</td></tr>
<tr><td>Notta</td><td>87%</td><td>93%</td><td>89%</td><td>81%</td><td>86%</td><td>84%</td></tr>
</tbody>
</table>

<h3>What the numbers mean</h3>
<ul>
<li><strong>On clean studio audio, everyone is good.</strong> The five tools cluster tightly at 93-96% on scripted narration. A difference of 3 percentage points on a 1,000-word transcript means 30 words different — usually filler phrases that don't change meaning. For podcast-style interviews, the cluster is similar at 89-93%.</li>
<li><strong>Noisy audio is where tools diverge.</strong> Gap widens to 8 percentage points (89% TranscriptX vs 81% Notta) on vlogs with background noise. This is where modern AI architectures (ours, Rev AI, Descript) pull ahead of older legacy captioning stacks.</li>
<li><strong>Technical content separates the field.</strong> Medical/legal/scientific jargon shows a 6-point gap (92% vs 86%). The difference is almost entirely in proper nouns and domain terminology. Tools trained on broader web audio handle "myocardial infarction" better than tools tuned on conversational English.</li>
<li><strong>Non-English is a real gap.</strong> Spanish and Japanese widen the gap to 7 points (91% vs 84%). For multilingual workflows this matters — a 7% higher error rate translates to 70 more errors per 1000 words, which is noticeable.</li>
</ul>

<h2>Where TranscriptX loses</h2>
<p>TranscriptX led on average but was not always best:</p>
<ul>
<li><strong>The Acquired podcast episode</strong> (2.5-hour interview, dense financial terminology): Rev AI scored 94%, TranscriptX 93%. The gap is small but real — Rev's model has better coverage of finance/business terminology.</li>
<li><strong>A Japanese YouTuber vlog</strong> (code-switching between Japanese and English): Descript scored 89%, TranscriptX 87%. Code-switching is genuinely hard; Descript's bilingual handling edged us here.</li>
<li><strong>A multi-speaker panel</strong> (4 speakers, often overlapping): Otter scored 86% with correct speaker labels; TranscriptX scored 90% but with no speaker separation. Depending on whether speaker labels matter more than raw accuracy for your use case, Otter's output may actually be more useful.</li>
</ul>

<h2>Failure modes observed</h2>
<h3>Most common errors across all tools</h3>
<ol>
<li><strong>Proper nouns.</strong> Names of people, places, companies, and products are frequently wrong on first transcription. This is inherent to AI transcription — a proper noun is a word the model has never seen in this exact context.</li>
<li><strong>Numbers and units.</strong> "17" vs "70," "five hundred" vs "500," "2.5 million" vs "2,500,000" — accuracy drops noticeably on numeric content.</li>
<li><strong>Overlapping speech.</strong> When two speakers talk over each other, all tools produce blended, partially correct text. Otter handles this best because of its speaker-separation pipeline, but even Otter loses words.</li>
<li><strong>Non-standard punctuation.</strong> All tools auto-punctuate; none match human punctuation exactly. We didn't count this as an error in WER.</li>
</ol>

<h3>Unique failure modes per tool</h3>
<ul>
<li><strong>TranscriptX:</strong> occasionally over-segments at natural pauses, producing many short segments where a single paragraph would be more readable. Word-level timestamps work; segment boundaries are sometimes awkward.</li>
<li><strong>Rev AI:</strong> tends to insert filler-word corrections that weren't in the original ("you know," "I mean") — sometimes adding words the speaker didn't say.</li>
<li><strong>Otter:</strong> struggles with technical jargon more than other tools; great at speaker separation but visibly weaker at domain vocabulary.</li>
<li><strong>Descript:</strong> occasionally drops very short utterances ("yeah," "right") that the model treated as non-speech.</li>
<li><strong>Notta:</strong> mid-sentence cuts on noisy audio produced the most fragmented output in the set.</li>
</ul>

<h2>What this means for your use case</h2>
<p>If your content is:</p>
<ul>
<li><strong>Clean studio audio in English:</strong> any of the 5 tools is fine. Pick on price, UX, and features — accuracy differences don't matter.</li>
<li><strong>Real-world recordings with noise:</strong> TranscriptX or Rev AI. The 6-8 point gap vs Otter/Notta matters on long content.</li>
<li><strong>Multi-speaker meetings:</strong> Otter, despite lower raw accuracy, because speaker labels offset the gap for most meeting use cases.</li>
<li><strong>Non-English content:</strong> TranscriptX. Not by a huge margin but consistently ahead on our Spanish and Japanese samples.</li>
<li><strong>Legal / medical / high-stakes:</strong> no AI tool in this set. Rev's human transcription tier (~99%) or similar is required. The WER gap between 93% and 99% is 6 points — in a 10,000-word deposition, that's 600 fewer errors.</li>
</ul>

<h2>How to reproduce this benchmark</h2>
<p>The 25 videos are publicly accessible. Email <a href="mailto:hello@transcriptx.xyz">hello@transcriptx.xyz</a> and we'll share the video URLs, our ground-truth transcripts, and the per-tool output we measured. If you find errors in our methodology or disagree with our corrections, send specifics — we'll correct the benchmark and note the change.</p>

<h2>Limitations</h2>
<ul>
<li>25 videos is a small sample. The confidence interval on individual tool accuracy is probably ±1-2 percentage points.</li>
<li>We tested default settings on each tool. Some tools have per-audio tuning (custom vocabularies, speaker enrollment) that would improve their scores — we didn't use these because typical users don't.</li>
<li>Tools update their models frequently. This benchmark is an April 2026 snapshot; numbers may have shifted by the time you read this. We re-run the benchmark quarterly.</li>
<li>We built TranscriptX. We made every effort to be honest with methodology and numbers, including publishing the cases where we lost. But we're not independent. Read accordingly.</li>
</ul>
""",
        "faq": [
            {
                "q": "How often is this benchmark updated?",
                "a": "Quarterly. The 'Updated' date at the top of the page is ground truth. Tools change their models frequently, so a 6-month-old benchmark should not be treated as current.",
            },
            {
                "q": "Why not test AssemblyAI or Deepgram?",
                "a": "We focused on consumer/SMB tools for this round. AssemblyAI and Deepgram are API-first products that most readers of this page won't use directly. We may add API-first tools in a future edition.",
            },
            {
                "q": "Are the differences statistically significant?",
                "a": "The gaps above 3 percentage points are almost certainly real. The 1-2 point gaps between closely-matched tools are within noise — on a different 25-video sample, the ordering could swap. Treat the headline numbers as directional, not definitive.",
            },
            {
                "q": "How did you handle multilingual audio?",
                "a": "Each tool was given the same URL / file and allowed to auto-detect language. In the bilingual English-Spanish sample, tools that handled code-switching received credit; tools that locked into one language and transcribed the other phonetically lost points.",
            },
            {
                "q": "What about timestamp accuracy?",
                "a": "Not measured in this benchmark — we focused on word error rate. All tools produced reasonable timestamps. Word-level timestamp fidelity is a separate benchmark we're planning for a future edition.",
            },
            {
                "q": "Why is TranscriptX on top?",
                "a": "We built it, and we optimized for the content types we tested. A third-party benchmark with a different test set might produce different numbers. This benchmark is as honest as we can make it, but read it with the awareness that we chose the test set.",
            },
        ],
    },
    "platform-support-index": {
        "slug": "platform-support-index",
        "title": "Every site we can transcribe a video from",
        "meta_title": "Sites We Support — 1000+ Video Sources | TranscriptX",
        "meta_description": "The full list of sites we can transcribe videos from — YouTube, TikTok, Instagram, Vimeo, and 1000+ more. Search to check if yours is on it before pasting a link.",
        "summary": "If you're not sure whether we support a particular site, search below. This list updates automatically whenever we add or remove a site.",
        "faq": [
            {
                "q": "How often does this list change?",
                "a": "It updates live — whenever we add or remove support for a site, this page reflects it. The \"Updated\" date at the top shows when the list was last synced.",
            },
            {
                "q": "Why do I see YouTube listed more than once (YouTube, YouTube Shorts, YouTube Playlist)?",
                "a": "Different URL types (a single video vs. a playlist vs. a Short) are handled slightly differently under the hood. You don't need to care — paste any YouTube link and it just works.",
            },
            {
                "q": "Can you add a site that's not on the list?",
                "a": "Usually yes. If a site has public videos and reasonably normal URLs, we can probably support it. Sites that require login, aggressively block automation, or change their URLs constantly are harder. Drop us a line with the site you need.",
            },
            {
                "q": "A site on the list isn't working for me — what do I do?",
                "a": "Sites change, and sometimes things break. Email us with the specific link that failed — if it's on our list, we treat fixes as a priority.",
            },
            {
                "q": "Are adult sites supported?",
                "a": "Some are in the list by default. We don't actively curate that part beyond removing obvious spam domains.",
            },
        ],
    },
    "transcript-repurposing-workflows": {
        "slug": "transcript-repurposing-workflows",
        "title": "Transcript Repurposing Workflows: 6 Patterns That Compound",
        "meta_title": "Transcript Repurposing Workflows for Content Teams | TranscriptX",
        "meta_description": "Six concrete workflows for turning video transcripts into blog posts, newsletters, social threads, SEO pages, and internal docs. Real templates and steps.",
        "summary": "Most teams that get serious about transcription realize the transcript itself isn't the asset — what you do with it downstream is. Six workflow patterns we see in teams that have figured this out, with concrete templates for each.",
        "body_html": """
<h2>Why transcripts alone aren't the asset</h2>
<p>If your workflow is "transcribe the video, save the transcript in a Drive folder," you're underusing the content. The transcript is raw material. What you do with it determines whether that material becomes a rounding error or a compounding engine for your team.</p>
<p>The teams we see getting real leverage out of transcription treat the transcript as an intermediate format — never the final deliverable. This page documents six patterns we've seen work, with concrete steps and templates.</p>

<h2>Pattern 1: Video → SEO article</h2>
<p>The most common workflow and still one of the highest-ROI. Every video your team publishes becomes a searchable page that attracts organic traffic over years, not hours.</p>
<h3>Steps</h3>
<ol>
<li>Transcribe the video (paste URL, export transcript).</li>
<li>Extract 3-5 explicit questions the video answers. These become H2/H3 headings in the article.</li>
<li>Restructure the transcript under each heading — pull relevant sections, compress filler.</li>
<li>Add an explicit "TL;DR" or "Quick answer" at the top.</li>
<li>Cite specific moments with timestamps ("at 12:34 the speaker says...").</li>
<li>Publish with a canonical link to the original video and a visible "This article was generated from our [X] video — watch it here" link.</li>
</ol>
<h3>What works</h3>
<p>Google treats video-sourced articles well when they add value (expand, contextualize, provide timestamps) rather than just publishing the raw transcript. The highest-ranking pages in this category are typically 800-1500 words with structured headings and specific quoted timestamps.</p>

<h2>Pattern 2: Podcast → show notes + newsletter</h2>
<p>Standard podcaster workflow: every episode becomes show notes + a newsletter edition. Transcripts are the input to both.</p>
<h3>Steps</h3>
<ol>
<li>Transcribe the episode with word-level timestamps.</li>
<li>Pull 5-10 quotes worth highlighting (insights, memorable moments, factual claims).</li>
<li>Write a 2-3 sentence episode summary at the top.</li>
<li>List discussion topics as bullet points with timestamps.</li>
<li>Embed 2-3 key quotes verbatim with speaker attribution.</li>
<li>Add any links/references mentioned in the episode.</li>
<li>Publish as show notes on your website. Re-format the same content as a newsletter issue.</li>
</ol>
<h3>What works</h3>
<p>Readers of podcast show notes are there because they want to reference the episode without re-listening. Timestamps on every quote make the notes useful for skimming. Newsletter versions do best when they lead with the strongest quote, not the summary.</p>

<h2>Pattern 3: Interview → social thread</h2>
<p>Lower-effort, higher-reach. Take a long interview, extract the most striking 5-8 moments, format as a Twitter/X thread or LinkedIn carousel.</p>
<h3>Steps</h3>
<ol>
<li>Transcribe the full interview.</li>
<li>Scan for quotable moments — specific claims, counterintuitive statements, concrete numbers.</li>
<li>Rewrite each quote for platform norms (max 280 characters per tweet; 1-2 sentences per LinkedIn slide).</li>
<li>Attribute the speaker and link back to the original video.</li>
<li>Post with a clear "link to full video" CTA in the last slot.</li>
</ol>
<h3>What works</h3>
<p>One 60-minute interview = 5-10 social posts. The full video might reach 10k people; extracted social content routinely reaches 10-100x more because short-form content compounds better on algorithmic feeds. The transcript is the research layer that makes the extraction fast.</p>

<h2>Pattern 4: Expert interview → internal knowledge base</h2>
<p>If your team interviews customers, subject-matter experts, or users regularly, transcripts feed into a searchable internal knowledge base. This is especially powerful for customer research, UX research, and compliance work.</p>
<h3>Steps</h3>
<ol>
<li>Transcribe every interview.</li>
<li>Store transcripts in a searchable system (Notion, Confluence, Google Drive, Airtable).</li>
<li>Tag each transcript by theme, interviewee role, date, and project.</li>
<li>Extract explicit quotes as atomic data points for later citation.</li>
<li>Build a periodic "what are customers telling us" report from tag-based searches.</li>
</ol>
<h3>What works</h3>
<p>Customer research teams that do this compound dramatically — by month six, every new question can be answered with "we talked to 15 customers who said X" instead of "let's run a new study." The transcript is the raw material that makes this possible.</p>

<h2>Pattern 5: Video essay → script for next video</h2>
<p>Creator-specific workflow. If you publish video essays, the transcript of each video is the draft for the next one — you can see what you said, find the weakest sections, and structure the follow-up around gaps in the original.</p>
<h3>Steps</h3>
<ol>
<li>Transcribe your own video after publishing.</li>
<li>Highlight sections that needed more depth or got the most reader questions.</li>
<li>Draft the follow-up video's outline around those gaps.</li>
<li>Use the original transcript as both a reference and a "don't repeat yourself" check.</li>
</ol>

<h2>Pattern 6: Meeting recording → action items + docs</h2>
<p>This is Otter's native territory but works fine with any transcription tool if you record meetings first. Every meeting becomes a document with action items extracted, decisions logged, and searchable history.</p>
<h3>Steps</h3>
<ol>
<li>Record meetings (Zoom, Meet, Teams).</li>
<li>Upload recording or paste URL into your transcription tool.</li>
<li>At the end of the transcript, add: "Action items," "Decisions made," "Open questions."</li>
<li>Extract specific to-dos with assignees into your project management tool.</li>
<li>Store the full transcript in a searchable doc.</li>
</ol>
<h3>What works</h3>
<p>This pattern only works if the recording and transcription are frictionless. If it takes 30 minutes to produce meeting notes, people skip it. Our URL-paste flow (or Otter's auto-join) makes this almost-free, which is what makes the habit sustainable.</p>

<h2>Tools for each pattern</h2>
<ul>
<li><strong>Transcription:</strong> TranscriptX (link-based, 1000+ platforms) or Otter (live meetings).</li>
<li><strong>Storage / search:</strong> Notion, Airtable, or a Google Drive folder with consistent naming.</li>
<li><strong>Content transformation:</strong> Claude, ChatGPT, or similar — feed the transcript in, ask for the specific output format.</li>
<li><strong>Publishing:</strong> whatever CMS you already use — WordPress, Ghost, Substack, LinkedIn.</li>
</ul>

<h2>The one thing that fails every time</h2>
<p>Publishing the raw transcript as a blog post. Don't do this. Transcripts are spoken language — they have verbal tics, tangents, and structural quirks that work in audio but don't work in prose. Every transcript-to-article workflow needs at least one restructuring pass. The tools compress hours of work into minutes, but they don't eliminate the need for human editorial judgment.</p>
""",
        "faq": [
            {
                "q": "Can I automate these workflows with AI?",
                "a": "Partially. Claude or GPT-4 can do a first pass on most transformations — transcript → article structure, transcript → social thread, transcript → show notes. You still need human review before publishing. The AI is fast at the structural work and unreliable on factual accuracy.",
            },
            {
                "q": "How long does transcript-to-article take in practice?",
                "a": "First draft: 30-45 minutes once you've done it a few times. Fully polished and edited: 2-3 hours. The speedup vs writing from scratch depends on how much of the content was already in the video — for a well-scripted talking-head video, 80%. For a meandering interview, less.",
            },
            {
                "q": "Should I publish the full transcript alongside the article?",
                "a": "Optional. Some creators include the full transcript as an appendix for accessibility and search. It doesn't hurt SEO if the article and transcript are clearly separated. Some creators publish transcript-only pages and the article-format page separately.",
            },
            {
                "q": "Is there a tool that automates the whole pipeline?",
                "a": "Not end-to-end, at quality. Descript does some of it (transcription + editing). Notion + Claude can stitch together a pipeline. The reliable pattern is: transcription tool (us/Otter) → AI structuring (Claude/GPT) → human edit → publish.",
            },
        ],
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


PLATFORM_CATEGORIES = {
    "video-streaming": {
        "slug": "video-streaming",
        "title": "Videos from YouTube, Vimeo, and other streaming sites",
        "meta_title": "Transcribe YouTube, Vimeo, Rumble Videos — 80+ Sites | TranscriptX",
        "meta_description": "Paste a link from YouTube, Vimeo, Dailymotion, Rumble, Bilibili, or dozens of other streaming sites. We'll turn it into text in under a minute.",
        "lede": "The big video sites. YouTube does most of the heavy lifting here, but we also handle Vimeo, Dailymotion, Rumble, and a long list of smaller streaming sites — paste any link and you get a transcript.",
        "match_keywords": ["youtube", "vimeo", "dailymotion", "bilibili", "niconico", "rumble", "odysee", "bitchute", "veoh", "metacafe", "viddler", "vbox", "dtube", "peertube"],
    },
    "social-media": {
        "slug": "social-media",
        "title": "Videos from TikTok, Instagram, X, and other social apps",
        "meta_title": "Transcribe TikTok, Instagram, X Videos — Paste Link | TranscriptX",
        "meta_description": "Grab the transcript of any TikTok, Instagram Reel, X video, Facebook post, or LinkedIn video. Paste the link, get text in seconds — no downloads needed.",
        "lede": "Transcribing short-form social video used to mean downloading it yourself, then uploading it somewhere. We skip both steps — paste a TikTok, Reel, X, or LinkedIn video link and you get the text back fast.",
        "match_keywords": ["tiktok", "instagram", "twitter", "x-twitter", "facebook", "reddit", "linkedin", "snapchat", "threads", "tumblr", "weibo", "kuaishou", "pinterest", "bluesky", "substack"],
    },
    "podcasts-audio": {
        "slug": "podcasts-audio",
        "title": "Podcast episodes and other audio",
        "meta_title": "Podcast Transcription — Apple, Spotify, SoundCloud | TranscriptX",
        "meta_description": "Paste a podcast episode link from Apple, Spotify, SoundCloud, or any RSS feed. Get a clean transcript with timestamps — perfect for show notes, clips, and quotes.",
        "lede": "Drop in a link to any podcast episode — Apple, Spotify, SoundCloud, your own RSS — and get a clean transcript back with timestamps. Great for show notes, pulling clips, or finding the moment your guest said something quotable. See <a href=\"/for/podcasters\">our page for podcasters</a> for the full workflow.",
        "match_keywords": ["soundcloud", "podcast", "applepodcasts", "spotify", "bandcamp", "mixcloud", "audible", "audiomack", "iheart", "stitcher", "podchaser", "podomatic", "anchor", "buzzsprout", "transistor", "castos", "simplecast", "megaphone"],
    },
    "live-streaming": {
        "slug": "live-streaming",
        "title": "Twitch streams, YouTube Lives, and other replays",
        "meta_title": "Transcribe Twitch & Live Stream Replays | TranscriptX",
        "meta_description": "Get the transcript of any Twitch VOD, YouTube Live replay, Kick stream, or other recorded livestream. Paste the link and get text — great for clipping highlights.",
        "lede": "We transcribe streams after they're over — Twitch VODs, YouTube Live replays, Kick streams, the lot. Great for finding highlight moments and pulling clips. For live captions as things are happening, you'd want Otter or a built-in stream tool instead.",
        "match_keywords": ["twitch", "kick", "youtube-live", "facebook-live", "instagram-live", "tiktok-live", "huya", "douyu", "afreeca", "bigo", "trovo", "dlive", "streamable", "livestream", "ustream", "periscope"],
    },
    "education": {
        "slug": "education",
        "title": "Online courses and lectures",
        "meta_title": "Transcribe Coursera, Khan Academy, TED & Course Videos | TranscriptX",
        "meta_description": "Turn online courses and lectures into searchable notes. Works with Coursera, edX, Khan Academy, TED, Udemy, and plenty more. Great for studying or referencing later.",
        "lede": "Lectures and course videos are some of the easiest content to transcribe — usually clean audio, one speaker, structured content. Drop in a Coursera, Khan Academy, TED, edX, or Udemy link and you have searchable notes in a minute.",
        "match_keywords": ["khanacademy", "coursera", "edx", "udemy", "skillshare", "ocw", "udacity", "lynda", "linkedin-learning", "pluralsight", "domestika", "masterclass", "ted", "tedx", "academic", "lecture"],
    },
    "news-media": {
        "slug": "news-media",
        "title": "News clips and broadcast segments",
        "meta_title": "Transcribe News Videos — BBC, CNN, Reuters, AP | TranscriptX",
        "meta_description": "Turn a news clip, press briefing, or broadcast segment into text you can quote and cite. BBC, CNN, Reuters, and loads of smaller outlets supported.",
        "lede": "Whether you're fact-checking a politician, pulling a quote for an article, or just want to read instead of watch — paste a news clip link (BBC, CNN, Reuters, or hundreds of regional outlets) and get the transcript. For the full reporter workflow, see <a href=\"/for/journalists\">our page for journalists</a>.",
        "match_keywords": ["bbc", "cnn", "reuters", "bloomberg", "aljazeera", "cbsnews", "abcnews", "nbcnews", "foxnews", "msnbc", "wsj", "ny-times", "washingtonpost", "guardian", "spiegel", "lemonde", "huffpost", "vice", "nbc", "abc", "cbs", "fox", "ap", "axs", "newsy", "news"],
    },
    "regional-asia": {
        "slug": "regional-asia",
        "title": "Videos from Bilibili, Douyin, Niconico, and other Asian sites",
        "meta_title": "Transcribe Bilibili, Douyin, Niconico, Naver Videos | TranscriptX",
        "meta_description": "Chinese, Japanese, and Korean video sites are fully supported — paste a link and we transcribe in the original language. Perfect for research or international work.",
        "lede": "Working with content from China, Japan, Korea, or elsewhere in Asia? Bilibili, Douyin, Niconico, Naver, Kakao — paste any link and get a transcript in the original language. 90+ languages supported.",
        "match_keywords": ["bilibili", "youku", "tudou", "iqiyi", "qqmusic", "kuwo", "netease", "douyin", "kuaishou", "weibo", "weibovideo", "xiaohongshu", "nicovideo", "niconico", "fc2", "showroom", "mirrativ", "openrec", "naver", "kakao", "afreeca", "vlive", "weverse"],
    },
    "regional-europe": {
        "slug": "regional-europe",
        "title": "Videos from BBC iPlayer, ARD, France TV, and other European sites",
        "meta_title": "Transcribe BBC iPlayer, ARD, France TV, RAI Videos | TranscriptX",
        "meta_description": "European broadcasters and streaming services — BBC iPlayer, ARD, ZDF, France Télévisions, RAI, RTVE, SVT, NRK, and more. Paste a link and get the transcript.",
        "lede": "Most European broadcasters only let you watch from inside their country. If you're there, paste away — BBC iPlayer, ARD, ZDF, France Télévisions, RAI, or whichever you need. If you hit a \"not available in your region\" message, <a href=\"/help/region-locked-video-transcript\">here's how to get around it</a>.",
        "match_keywords": ["bbc", "iplayer", "arte", "ard", "zdf", "francetv", "francetvinfo", "rai", "rtve", "npo", "nrk", "svtplay", "svt", "yle", "drtv", "kommunetv", "rtbf", "vrt", "ceskatelevize", "rt", "tv2", "tv4", "lcp", "europa", "europarl", "bundestag", "ndr", "wdr", "mdr", "br", "swr", "rbb", "hr", "sr", "sat1"],
    },
    "creators-paid": {
        "slug": "creators-paid",
        "title": "Your own Patreon, Substack, or Nebula videos",
        "meta_title": "Transcribe Patreon, Substack, Nebula Videos | TranscriptX",
        "meta_description": "Repurpose your own paid content — Patreon, Substack, Nebula, Floatplane — into show notes, articles, and clips. Public posts paste directly; paywalled ones need a workaround.",
        "lede": "If you publish paid content on Patreon, Substack, Nebula, or Floatplane, transcribing your own videos turns them into show notes, blog posts, or social clips fast. Your public-tier posts paste directly; paywalled ones need an extra step — <a href=\"/help/private-video-transcript\">here's how</a>.",
        "match_keywords": ["patreon", "substack", "nebula", "memberful", "floatplane", "ko-fi", "podia", "teachable", "thinkific", "kajabi", "skool", "circle", "discord", "twitch-subscriber"],
    },
    "cloud-storage": {
        "slug": "cloud-storage",
        "title": "Files on Google Drive, Dropbox, or OneDrive",
        "meta_title": "Transcribe Videos on Google Drive, Dropbox, OneDrive | TranscriptX",
        "meta_description": "Got a video on Drive, Dropbox, or OneDrive? Paste the file link (not the folder link — that's the most common mistake). Full guide inside.",
        "lede": "Have a video sitting in your Drive, Dropbox, or OneDrive? Paste the file link and we'll transcribe it. The #1 mistake people make is pasting the <em>folder</em> link instead of the <em>file</em> link — <a href=\"/help/google-drive-transcript-link\">here's exactly how to get the right one</a>. Full file-upload guide <a href=\"/help/upload-audio-file-transcript\">here</a>.",
        "match_keywords": ["googledrive", "dropbox", "onedrive", "box", "icloud", "mega", "wetransfer", "pcloud", "sync", "owncloud", "nextcloud"],
    },
    "enterprise-meetings": {
        "slug": "enterprise-meetings",
        "title": "Zoom recordings, Loom videos, and other work stuff",
        "meta_title": "Transcribe Zoom Recordings, Loom, Wistia, Webex | TranscriptX",
        "meta_description": "Transcribe Zoom recordings, Loom videos, Webex sessions, Wistia-hosted explainers, and more. Perfect for turning meetings into searchable notes after the fact.",
        "lede": "Meeting recorded on Zoom or Teams? Explainer on Loom or Wistia? Training video on Panopto? Paste the link (or upload the Zoom recording to Drive first) and get the transcript. For live meetings as they happen, Otter is the better tool — we handle the ones you've already recorded.",
        "match_keywords": ["zoom", "webex", "teams", "loom", "wistia", "vidyard", "brightcove", "kaltura", "panopto", "vimeo-pro", "vimeo-business", "vimeo-enterprise", "ringcentral", "gotomeeting", "bluejeans", "jitsi", "8x8"],
    },
    "music-audio-podcast": {
        "slug": "music-audio-podcast",
        "title": "Music videos and audio from Spotify, Apple Music, and more",
        "meta_title": "Transcribe Music & Music Podcast Content | TranscriptX",
        "meta_description": "Music-related video and podcast content from Spotify, Apple Music, SoundCloud, YouTube Music, and more. Note: we're built for speech — song lyrics get less accurate results.",
        "lede": "For music-related videos, podcasts, and interviews hosted on music platforms — we handle those well. Pure song-lyric transcription is tougher because our engine is trained on speech, not singing. For lyrics specifically, a dedicated lyric tool will do better.",
        "match_keywords": ["youtube-music", "spotify", "apple-music", "tidal", "deezer", "audius", "qobuz", "qq-music", "netease-music", "yandexmusic", "soundcloud", "bandcamp", "jamendo", "monstercat", "mixcloud", "pandora"],
    },
}


def categorize_platform(slug):
    """Return the category slug a platform belongs to, or None if uncategorized."""
    if not slug:
        return None
    s = slug.lower()
    # Check each category's match_keywords. First match wins.
    for cat_slug, cat in PLATFORM_CATEGORIES.items():
        for kw in cat.get("match_keywords", []):
            if kw in s:
                return cat_slug
    return None


def get_platforms_by_category(category_slug):
    """Return the list of platform pages that belong to a category, sorted by name."""
    pages = get_platform_pages()
    matched = [p for slug, p in pages.items() if categorize_platform(slug) == category_slug]
    return sorted(matched, key=lambda p: (p.get("display_name") or "").lower())


def current_lastmod():
    return datetime.now(timezone.utc).date().isoformat()


def get_static_seo_paths():
    paths = [page["path"] for page in HEAD_TERM_PAGES.values()]
    paths.extend([f"/compare/{slug}" for slug in COMPARISON_PAGES])
    paths.extend([f"/research/{slug}" for slug in RESEARCH_PAGES])
    paths.extend([f"/help/{slug}" for slug in HELP_PAGES])
    paths.extend([f"/for/{slug}" for slug in PERSONA_PAGES])
    paths.extend([f"/category/{slug}" for slug in PLATFORM_CATEGORIES])
    paths.append("/help")
    paths.append("/categories")
    paths.append("/press-kit")
    return paths
