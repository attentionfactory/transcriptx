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


PLATFORM_GUIDES = {
    "pinterest": {
        "slug": "pinterest",
        "display": "Pinterest",
        "title": "How to Transcribe a Pinterest Video or Idea Pin",
        "h1": "How to Transcribe a Pinterest Video or Idea Pin",
        "meta_title": "Transcribe Pinterest Video — Idea Pin to Text (Free) | TranscriptX",
        "meta_description": "Pinterest doesn't let you export captions. Copy the Pin URL, paste it into TranscriptX. Works on public video Pins and Idea Pins — under a minute.",
        "quick_answer": "Open the video Pin on Pinterest, copy the URL from the browser (or tap Share → Copy link in the app), paste it on TranscriptX. Works on public Pins and Idea Pins. Secret boards and private accounts won't work.",
        "url_example": "https://pinterest.com/pin/1234567890/",
        "steps": [
            {
                "heading": "Open the Pin on Pinterest",
                "body": "On pinterest.com, click the video Pin to open its detail view. On mobile, tap the Pin to expand it. You want the single-Pin view, not the board or profile feed.",
                "screenshot": "Pinterest Pin detail view with the video player and share buttons visible",
            },
            {
                "heading": "Copy the Pin URL",
                "body": "On desktop, copy the URL from the browser — it looks like <code>pinterest.com/pin/1234567890/</code>. On mobile, tap the Share arrow → Copy link. The short <code>pin.it/abc123</code> format also works.",
                "screenshot": "Pinterest mobile Share menu with Copy link highlighted",
            },
            {
                "heading": "Paste into TranscriptX",
                "body": "Open <a href=\"/\">transcriptx.xyz</a>, paste the Pin URL, hit Transcribe. Under a minute for most Pins — Idea Pins with multiple video pages take a bit longer.",
                "screenshot": None,
            },
        ],
        "breaks": [
            {
                "title": "Secret board Pin",
                "body": "Secret boards require a Pinterest login. Our servers can't get in. Move the Pin to a public board temporarily, transcribe, then move it back.",
            },
            {
                "title": "Private account Pin",
                "body": "Private accounts require approved followers. We don't have an account. If it's yours, flip to public briefly or re-Pin to a public board.",
            },
            {
                "title": "Music-only Idea Pin",
                "body": "Lots of Idea Pins are soundtrack over visuals with no spoken audio. No speech = empty transcript. Expected.",
            },
            {
                "title": "Multi-page Idea Pin",
                "body": "If only some pages have spoken audio, you'll get a transcript of the audio portions. If pages have separate audio tracks, they transcribe as one continuous stream.",
            },
            {
                "title": "Pinterest TV or live content",
                "body": "Pinterest TV episodes work once the replay is saved. Live streams that haven't been archived aren't reachable — wait for the replay.",
            },
            {
                "title": "Country-blocked commercial Pin",
                "body": "Rare, but some paid-partnership Pins are geo-restricted. Our servers are in the US. If the Pin doesn't play for a US viewer, we can't transcribe it.",
            },
        ],
        "faqs": [
            {
                "q": "Can you transcribe Idea Pins with multiple pages?",
                "a": "Yes. Each page's audio is transcribed in order and returned as a single transcript. Pages without spoken audio produce an empty segment and we skip them.",
            },
            {
                "q": "What about Pinterest videos with no captions?",
                "a": "Pinterest rarely provides captions at all — which is why this guide exists. We run Whisper on the actual audio track, so caption presence doesn't matter.",
            },
            {
                "q": "Does the pin.it short link work?",
                "a": "Yes. We resolve the short link to the canonical Pin URL before fetching. Either format works.",
            },
            {
                "q": "Will it capture the music in a Pin?",
                "a": "No. Whisper transcribes spoken language, not song lyrics. Music gets ignored. If a Pin is all music with no voice-over, you'll get an empty transcript.",
            },
            {
                "q": "What if my Pin is on a shared board I was invited to?",
                "a": "Shared boards behave like public boards as long as the owner has set the board to public. If it's set to secret or collaborators-only, our servers can't reach it.",
            },
        ],
        "related_slugs": [
            "transcribe-tiktok-video",
            "transcribe-instagram-reel-or-story",
            "transcribe-youtube-short",
        ],
    },
    "rumble": {
        "slug": "rumble",
        "display": "Rumble",
        "title": "How to Transcribe a Rumble Video",
        "h1": "How to Transcribe a Rumble Video",
        "meta_title": "Transcribe Rumble Video — Paste the Link, Get Text (Free) | TranscriptX",
        "meta_description": "Rumble doesn't expose a clean caption download. Copy the Rumble URL, paste it on TranscriptX, get the transcript in about a minute.",
        "quick_answer": "Open the Rumble video page, copy the URL from the browser, paste it on TranscriptX. Works on any public Rumble video. Rumble+ locked videos and age-gated content won't work from our servers.",
        "url_example": "https://rumble.com/v4abc12-title-of-the-video.html",
        "steps": [
            {"heading": "Open the Rumble page", "body": "On rumble.com, open the video you want. The URL in your browser is what you need — you don't need an account.", "screenshot": None},
            {"heading": "Copy the URL", "body": "URL format is <code>rumble.com/v4abc12-title-of-the-video.html</code>. The embed URL (<code>rumble.com/embed/v4abc12/</code>) also works.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop the URL on <a href=\"/\">transcriptx.xyz</a>, hit Transcribe. Long streams take a few minutes.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Rumble+ locked video", "body": "Premium-tier Rumble+ content requires a paid login. We can't subscribe for you."},
            {"title": "Age-gated content", "body": "Rumble's 18+ videos need a confirmed-adult session. Our servers don't have one."},
            {"title": "Deleted or removed video", "body": "If Rumble pulled the video for policy reasons, the URL returns 404 for us too."},
            {"title": "Embed-only live stream", "body": "Live streams that haven't been saved as VODs can't be fetched. Wait for the replay to post."},
        ],
        "faqs": [
            {"q": "Does it work for Rumble live streams?", "a": "Only after the live ends and the VOD is posted. Live streams in progress aren't transcribable — we need a completed recording."},
            {"q": "Are the captions Rumble shows the same as your transcript?", "a": "No. Rumble sometimes shows basic auto-captions that you can't cleanly export. We run Whisper on the actual audio, which is more accurate and gives you the text in a downloadable format."},
            {"q": "What about Rumble Cloud hosted videos from a different domain?", "a": "If the video is publicly viewable at a Rumble URL, it works. Custom-domain Rumble Cloud videos sometimes do, sometimes don't — paste and see."},
        ],
        "related_slugs": ["transcribe-private-youtube-video", "transcribe-twitch-vod-or-clip"],
    },
    "dailymotion": {
        "slug": "dailymotion",
        "display": "Dailymotion",
        "title": "How to Transcribe a Dailymotion Video",
        "h1": "How to Transcribe a Dailymotion Video",
        "meta_title": "Transcribe Dailymotion Video — Paste the URL, Done | TranscriptX",
        "meta_description": "Copy the Dailymotion URL, paste it on TranscriptX. Cleaner captions than Dailymotion's built-in, downloadable in text or SRT. Free on our starter tier.",
        "quick_answer": "Paste the Dailymotion video URL on TranscriptX. Works on any public video. Partner-only, paywalled, and some region-locked content won't work from our US servers.",
        "url_example": "https://www.dailymotion.com/video/x8abc12",
        "steps": [
            {"heading": "Open the Dailymotion video", "body": "On dailymotion.com, open the video. Copy the URL from the browser.", "screenshot": None},
            {"heading": "URL format check", "body": "Standard format is <code>dailymotion.com/video/x8abc12</code>. Share-shortened <code>dai.ly/x8abc12</code> also works.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop the URL on <a href=\"/\">transcriptx.xyz</a> and hit Transcribe.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Region-locked video", "body": "Rights-holder restrictions on Dailymotion's French-origin content occasionally block US viewing. If it won't play in a US incognito window, we can't reach it either."},
            {"title": "Partner-only / paywalled", "body": "Premium channels behind Dailymotion's paywall require authentication we don't have."},
            {"title": "Age-gated (18+)", "body": "Requires a signed-in adult session. Not supported."},
            {"title": "Embedded-only videos", "body": "Some Dailymotion videos are set to play only inside specific partner sites. Direct URLs return a 403."},
        ],
        "faqs": [
            {"q": "Does Dailymotion give you transcripts directly?", "a": "Not publicly. Some Dailymotion videos have captions, but there's no official download path. We transcribe from the audio track."},
            {"q": "What languages work well?", "a": "Dailymotion skews European — French, Spanish, German, Portuguese, Italian all transcribe well with Whisper. Auto-detect gets the right one almost always, but if it misses, use the free language retry on the result card."},
            {"q": "Works on news clips?", "a": "Yes. News channels are one of the most common Dailymotion use cases and they transcribe cleanly."},
        ],
        "related_slugs": ["transcribe-foreign-language-video", "transcribe-vimeo-video"],
    },
    "wistia": {
        "slug": "wistia",
        "display": "Wistia",
        "title": "How to Transcribe a Wistia Video",
        "h1": "How to Transcribe a Wistia Video",
        "meta_title": "Transcribe Wistia Video — Business Video to Text | TranscriptX",
        "meta_description": "Wistia is built for business video. Captions cost extra. TranscriptX transcribes any public Wistia URL for free on the starter tier.",
        "quick_answer": "Copy the Wistia video URL (from a public media page or embed), paste on TranscriptX. Works for public videos. Password-protected videos need the password removed, and Wistia Channels with domain-restricted embeds won't open.",
        "url_example": "https://owner.wistia.com/medias/abc12xyz34",
        "steps": [
            {"heading": "Find the Wistia video URL", "body": "If you own the video, open it in your Wistia dashboard and copy the public share URL. If you're watching an embedded Wistia video on a third-party site, click the player's title — it usually links to the media page at <code>owner.wistia.com/medias/...</code>.", "screenshot": None},
            {"heading": "Remove password protection temporarily", "body": "If the video is password-protected, you'll need to remove the password for the retry — our servers can't type it. Re-add the password after.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop the URL on <a href=\"/\">transcriptx.xyz</a>, hit Transcribe.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Password-protected video", "body": "Wistia's password wall requires typed input. Remove the password, transcribe, re-add it."},
            {"title": "Domain-restricted embed", "body": "Wistia lets you restrict playback to specific domains. If the restriction is on, our servers can't play the video from outside those domains."},
            {"title": "Private Channel or Series", "body": "Channels set to private require viewer auth. Not supported — contact the owner for a public share link."},
            {"title": "Captions paywalled on your plan", "body": "Wistia's own captions are a paid add-on. This is actually why most Wistia users come to us — skip that fee."},
        ],
        "faqs": [
            {"q": "Is Wistia's built-in caption feature different?", "a": "Wistia's captions cost extra per video on most plans. We run Whisper for a flat subscription fee — typically cheaper if you have more than a handful of videos."},
            {"q": "Does this work for Soapbox recordings uploaded to Wistia?", "a": "Yes. Soapbox videos uploaded into Wistia get the same share URL pattern. Paste and go."},
            {"q": "What about Wistia Live?", "a": "Only after the live stream ends and the recording is saved to the library. Live events in progress can't be transcribed."},
        ],
        "related_slugs": ["transcribe-loom-video", "transcribe-vimeo-video", "transcribe-webinar-for-blog"],
    },
    "streamable": {
        "slug": "streamable",
        "display": "Streamable",
        "title": "How to Transcribe a Streamable Video",
        "h1": "How to Transcribe a Streamable Video",
        "meta_title": "Transcribe Streamable Video — Short Clips to Text | TranscriptX",
        "meta_description": "Streamable clips often have no captions at all. Copy the streamable.com URL, paste on TranscriptX, get a transcript in under a minute.",
        "quick_answer": "Copy the Streamable URL (streamable.com/ABC123), paste on TranscriptX. Works on any public clip. Free-tier clips that expired after 90 days are gone — check the link plays in an incognito window first.",
        "url_example": "https://streamable.com/abc123",
        "steps": [
            {"heading": "Open the Streamable link", "body": "Paste the URL in your browser first to confirm it plays. Streamable free-tier clips expire after 90 days — if it's gone for you, it's gone for us.", "screenshot": None},
            {"heading": "Copy the URL", "body": "Format is <code>streamable.com/abc123</code>. Short, clean — nothing to clean up.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop it on <a href=\"/\">transcriptx.xyz</a> and hit Transcribe. Clips are usually short, so transcripts come back in seconds.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Expired clip", "body": "Free Streamable accounts delete uploads after 90 days. If the link 404s in your browser, the clip's gone for us too."},
            {"title": "Password-protected clip", "body": "Paid Streamable accounts can lock clips with a password. We can't type it. Owner has to disable the password."},
            {"title": "Flagged / under review", "body": "Streamable occasionally pulls clips for review after upload. Retry later or have the owner re-upload."},
            {"title": "Music-only clip", "body": "Lots of Streamable clips are silent GIF-style or music-only. No speech = empty transcript."},
        ],
        "faqs": [
            {"q": "Does this work for Streamable premium / branded clips?", "a": "Yes, as long as the clip is publicly viewable. Watermarks and custom branding don't affect our ability to transcribe."},
            {"q": "Can I transcribe lots of Streamable clips at once?", "a": "Yes, on our batch tier. Paste one URL per line and we process them in parallel."},
            {"q": "What about the old Streamable CDN URLs (cdn.streamable.com)?", "a": "The standard streamable.com page URL is more reliable — we follow the redirect from there. Direct CDN URLs sometimes work, sometimes 403."},
        ],
        "related_slugs": ["transcribe-reddit-video", "transcribe-youtube-short"],
    },
    "kick": {
        "slug": "kick",
        "display": "Kick",
        "title": "How to Transcribe a Kick VOD or Clip",
        "h1": "How to Transcribe a Kick VOD or Clip",
        "meta_title": "Transcribe Kick.com VOD or Clip — Stream to Text | TranscriptX",
        "meta_description": "Kick.com doesn't export captions. Copy the VOD or clip URL, paste on TranscriptX. For YouTube reuploads, sponsor reports, or compliance archives.",
        "quick_answer": "Copy the Kick VOD URL (kick.com/video/UUID) or clip URL, paste on TranscriptX. Works for public VODs and clips. Subscriber-only content requires authentication we don't have.",
        "url_example": "https://kick.com/video/abc12-uuid",
        "steps": [
            {"heading": "Find the VOD or clip on Kick", "body": "On kick.com, go to the streamer's channel → Videos or Clips, open the one you want.", "screenshot": None},
            {"heading": "Copy the URL", "body": "VODs look like <code>kick.com/video/UUID</code>, clips look like <code>kick.com/STREAMER?clip=abc123</code>. Both work.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop on <a href=\"/\">transcriptx.xyz</a>. Multi-hour VODs take proportionally longer.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Subscriber-only VOD", "body": "Kick lets streamers restrict VODs to paid subscribers. We can't subscribe for you."},
            {"title": "VOD deleted by streamer", "body": "Streamers delete VODs all the time. If gone from their channel, it's gone for us."},
            {"title": "Age-gated (18+ mature) stream", "body": "Requires a confirmed-adult Kick account. Not supported."},
            {"title": "DMCA-muted sections", "body": "If Kick muted audio for copyright reasons, those sections produce no transcript (silence)."},
        ],
        "faqs": [
            {"q": "Is Kick different from Twitch for this workflow?", "a": "Same pattern: VODs paste as URLs, clips paste as URLs, live streams need to end first. Implementation details differ but the user flow is identical."},
            {"q": "Can I transcribe the chat?", "a": "No. This transcribes the streamer's audio only. Chat is a separate data stream."},
            {"q": "What if a Kick stream is happening right now?", "a": "Wait until the stream ends and the VOD posts. We need a completed recording — real-time live transcription isn't supported."},
        ],
        "related_slugs": ["transcribe-twitch-vod-or-clip", "youtube-video-to-show-notes"],
    },
    "twitch-live": {
        "slug": "twitch-live",
        "display": "Twitch Live",
        "title": "How to Transcribe a Twitch Live Stream (Once It Ends)",
        "h1": "How to Transcribe a Twitch Live Stream (Once It Ends)",
        "meta_title": "Transcribe Twitch Live Stream — Wait for the VOD | TranscriptX",
        "meta_description": "You can't transcribe a Twitch stream while it's live, but the VOD works cleanly once the stream ends. Here's the path and the common gotchas.",
        "quick_answer": "Twitch live streams can't be transcribed in real-time — we need the recorded VOD. After the stream ends, grab the VOD URL from the streamer's channel → Videos tab and paste it into TranscriptX. VODs expire after 7-60 days depending on the streamer's tier, so don't wait.",
        "url_example": "https://twitch.tv/videos/123456789",
        "steps": [
            {"heading": "Wait for the stream to end", "body": "Live transcription isn't supported — we fetch and process a complete audio file. You need the saved recording.", "screenshot": None},
            {"heading": "Find the VOD", "body": "Go to the streamer's Twitch channel → click <strong>Videos</strong>. The most recent stream appears at the top. Open it.", "screenshot": None},
            {"heading": "Paste the VOD URL", "body": "URL looks like <code>twitch.tv/videos/123456789</code>. Drop it on <a href=\"/\">transcriptx.xyz</a>. 6-hour streams take a few minutes.", "screenshot": None},
        ],
        "breaks": [
            {"title": "VOD expired", "body": "Partners: 60 days. Affiliates: 14 days. Regular users: 7 days. Past the retention window, the VOD is gone."},
            {"title": "Streamer disabled VOD saving", "body": "Some streamers turn off auto-save. If there's no VOD on the Videos tab after the stream ends, the recording doesn't exist."},
            {"title": "Subscriber-only VOD", "body": "Paywalled — we can't subscribe."},
            {"title": "DMCA-muted audio chunks", "body": "Twitch mutes sections with copyright strikes. Muted segments transcribe as silence (empty)."},
        ],
        "faqs": [
            {"q": "Why can't you transcribe a live stream in real-time?", "a": "Real-time transcription is a different product category — it needs low-latency audio capture and a different processing pipeline. We transcribe completed audio files. For live captioning, use Twitch's own caption feature or a service designed for it."},
            {"q": "Can I transcribe Highlights instead of VODs?", "a": "Yes. Highlights are saved segments with a permanent URL. The pattern is the same: copy the URL, paste."},
            {"q": "What's the difference between this guide and the Twitch VOD guide?", "a": "The other guide covers VODs and clips in general. This one focuses on the live-to-VOD workflow specifically — the wait, the retention cliff, and where VODs disappear to."},
        ],
        "related_slugs": ["transcribe-twitch-vod-or-clip", "youtube-video-to-show-notes"],
    },
    "linkedin-video": {
        "slug": "linkedin-video",
        "display": "LinkedIn video",
        "title": "How to Transcribe a LinkedIn Video Post",
        "h1": "How to Transcribe a LinkedIn Video Post",
        "meta_title": "Transcribe LinkedIn Video Post — Copy URL, Paste | TranscriptX",
        "meta_description": "LinkedIn video posts don't export captions cleanly. Copy the post URL, paste on TranscriptX, get the full transcript for repurposing or citations.",
        "quick_answer": "Open the LinkedIn post with the video, click the timestamp (\"2h ago\", \"1d ago\") to open it as a standalone page, copy the URL, paste on TranscriptX. Works on public posts. Connection-only posts and private Company Page content won't open from our servers.",
        "url_example": "https://linkedin.com/posts/username_topic-activity-7123456789",
        "steps": [
            {"heading": "Open the post as a standalone page", "body": "Click the timestamp under the post (\"2h\", \"1d ago\") to open it at its own URL. This is critical — the feed URL doesn't point at a specific post.", "screenshot": None},
            {"heading": "Copy the URL from the browser", "body": "Format is <code>linkedin.com/posts/username_topic-activity-7123456789</code>. The <code>-activity-</code> segment is the post ID.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop the URL on <a href=\"/\">transcriptx.xyz</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Connection-only or private post", "body": "LinkedIn lets users post to connections-only, which requires a connection relationship with the poster. We can't establish that."},
            {"title": "Company Page restricted access", "body": "Some Company Pages require employee verification to view. We're not an employee."},
            {"title": "Deleted post", "body": "Common on LinkedIn — posters edit or delete often. If the URL 404s now, the post is gone."},
            {"title": "Article-embedded video vs post video", "body": "LinkedIn Articles (long-form) embed videos differently than feed posts. If an Article URL fails, grab the video's own URL from inside the Article instead."},
        ],
        "faqs": [
            {"q": "Does LinkedIn provide captions?", "a": "Sometimes auto-generated, but export is clunky and incomplete. We run Whisper on the audio for a cleaner transcript."},
            {"q": "What about LinkedIn Live recordings?", "a": "See our <a href=\"/how-to-transcribe/linkedin-live\">LinkedIn Live guide</a> — different URL pattern, different gotchas."},
            {"q": "Can I transcribe a LinkedIn video I DM'd someone?", "a": "No. DMs are behind your personal login and not accessible to external tools."},
        ],
        "related_slugs": ["transcribe-webinar-for-blog", "transcribe-sales-call-for-research"],
    },
    "linkedin-live": {
        "slug": "linkedin-live",
        "display": "LinkedIn Live",
        "title": "How to Transcribe a LinkedIn Live Recording",
        "h1": "How to Transcribe a LinkedIn Live Recording",
        "meta_title": "Transcribe LinkedIn Live Event — Recorded Stream to Text | TranscriptX",
        "meta_description": "Only LinkedIn Live recordings are transcribable — live streams in progress aren't. Here's where to find the recording and how to paste.",
        "quick_answer": "LinkedIn Live events aren't transcribable while live. After the event, the host has a window where the recording is available as a post on their profile — copy that post's URL and paste on TranscriptX. If the host didn't save the recording, it's gone.",
        "url_example": "https://linkedin.com/events/7123456789",
        "steps": [
            {"heading": "Find the saved recording", "body": "After a LinkedIn Live event, the replay usually posts on the host's profile automatically. Go to their profile → Activity → find the event post.", "screenshot": None},
            {"heading": "Click the timestamp to get a direct URL", "body": "As with any LinkedIn post, click the timestamp (\"2d ago\") to open it at its own URL. Copy that URL.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste → Transcribe. Multi-hour events take proportionally longer.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Host didn't save the recording", "body": "LinkedIn Live events don't auto-save permanently. If the host opted not to post the replay, you can't recover it."},
            {"title": "Event still live", "body": "Live events can't be transcribed while they're happening. Wait for the event to end and the replay to post."},
            {"title": "Registration-gated replay", "body": "Some LinkedIn Live events lock the replay to registrants only. Requires authenticated access we don't have."},
            {"title": "Connection-only replay post", "body": "If the host posted the replay as connections-only, our servers can't access it."},
        ],
        "faqs": [
            {"q": "Can I transcribe while the event is live?", "a": "No. We need a completed audio file. Live real-time captioning is a different product category."},
            {"q": "How long does LinkedIn keep the replay?", "a": "Until the host deletes it. There's no auto-expiration, but hosts often clean up old events."},
            {"q": "Does it work for LinkedIn Learning videos?", "a": "No. LinkedIn Learning is behind the paid LinkedIn Premium wall."},
        ],
        "related_slugs": ["transcribe-webinar-for-blog", "linkedin-video"],
    },
    "x-video-post": {
        "slug": "x-video-post",
        "display": "X (Twitter) video post",
        "title": "How to Transcribe a Video on X (Twitter)",
        "h1": "How to Transcribe a Video on X (Twitter)",
        "meta_title": "Transcribe X / Twitter Video — Paste the Tweet URL | TranscriptX",
        "meta_description": "Videos attached to X posts don't have downloadable captions. Copy the tweet URL, paste on TranscriptX. Not for Spaces — see the Spaces guide for that.",
        "quick_answer": "Open the X post with the video, copy the URL from the browser (x.com/user/status/123...), paste on TranscriptX. Works on public account videos. Protected accounts, age-gated content, and videos inside DMs don't work.",
        "url_example": "https://x.com/username/status/1234567890",
        "steps": [
            {"heading": "Open the post in a browser", "body": "On x.com, click the post timestamp to open it as a standalone page. Mobile app share sheets sometimes drop context — desktop is more reliable.", "screenshot": None},
            {"heading": "Copy the URL", "body": "Format is <code>x.com/username/status/1234567890</code>. The old <code>twitter.com/</code> URLs also work — X redirects them.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste. Short clips come back in seconds.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Protected account", "body": "If the account is set to Protected, only approved followers can see posts. Our servers aren't followers. If it's yours, unlock for a moment."},
            {"title": "Age-gated (sensitive content)", "body": "X gates sensitive content behind a signed-in adult session. Not supported."},
            {"title": "Deleted post", "body": "Very common on X. If the post is gone, it's gone for us."},
            {"title": "Video inside a DM or Communities-only post", "body": "DMs and community-gated content require authenticated access we don't have."},
        ],
        "faqs": [
            {"q": "Is this the same as Spaces?", "a": "No. Spaces are audio rooms — see our <a href=\"/guides/transcribe-x-spaces-recording\">X Spaces guide</a>. This guide is for videos attached to posts."},
            {"q": "What about X Premium (formerly Blue) video uploads?", "a": "Longer videos from Premium accounts work the same — paste the post URL."},
            {"q": "What if the post has multiple videos?", "a": "We transcribe the first video attached. For multi-video posts, submit each one individually by grabbing the video-specific URL (click the video, copy the address)."},
        ],
        "related_slugs": ["transcribe-x-spaces-recording", "transcribe-facebook-video"],
    },
    "panopto": {
        "slug": "panopto",
        "display": "Panopto",
        "title": "How to Transcribe a Panopto Video (Lectures, Training, Webinars)",
        "h1": "How to Transcribe a Panopto Video",
        "meta_title": "Transcribe Panopto Video — Lecture or Training to Text | TranscriptX",
        "meta_description": "Panopto videos are usually behind SSO. If you have a public share link, paste it. If not, here's how to work around the org login wall.",
        "quick_answer": "If the Panopto video has a public share link (Anyone with the link), paste the URL on TranscriptX. If it's SSO-locked to your org, you'll need to ask the instructor for a public link or download the video locally first.",
        "url_example": "https://university.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=GUID",
        "steps": [
            {"heading": "Check the share setting", "body": "Open the Panopto video → Share (or Settings if it's your own video). Confirm access is set to <strong>Anyone with the link</strong>, not <strong>Signed-in users only</strong>.", "screenshot": None},
            {"heading": "Copy the viewer URL", "body": "Format is <code>YOUR_ORG.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=GUID</code>. The Embed URL also works but the Viewer URL is more reliable.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop on <a href=\"/\">transcriptx.xyz</a>. Lectures tend to be long — 1-2 hours is normal — so expect a few minutes of processing.", "screenshot": None},
        ],
        "breaks": [
            {"title": "SSO-locked to your organization", "body": "Most Panopto videos default to \"Signed-in users only\" or \"My organization\". We can't sign in. Ask the instructor or IT admin to switch the specific video to <strong>Anyone with the link</strong>."},
            {"title": "Scheduled-expiration share", "body": "Panopto share links can be set to expire. If the link was live yesterday and fails today, the expiration window passed."},
            {"title": "Edited segments with missing audio", "body": "Instructors sometimes redact sections for FERPA or copyright. Redacted segments produce silent gaps in the transcript."},
            {"title": "Recording still processing", "body": "Immediately after a live lecture ends, Panopto transcodes for up to an hour. Try again after the processing icon disappears."},
        ],
        "faqs": [
            {"q": "Doesn't Panopto have built-in captioning?", "a": "It's an add-on that requires admin enablement and costs extra per minute. Most institutions don't enable it on every video. We're the workaround when Panopto's captions aren't available."},
            {"q": "My org uses Panopto through Canvas / Moodle / Blackboard — does that matter?", "a": "Only the share setting matters. If the video is \"Anyone with the link\", the LMS wrapper is irrelevant — paste the Panopto viewer URL directly."},
            {"q": "What if my instructor won't make it public?", "a": "Last resort: download the video (Panopto has a download option if enabled), upload to Drive with Anyone-with-the-link, and paste that Drive URL instead. See <a href=\"/guides/transcribe-google-drive-video\">our Google Drive guide</a>."},
        ],
        "related_slugs": ["transcribe-lecture-for-study-notes", "transcribe-zoom-recording", "transcribe-google-drive-video"],
    },
    "kaltura": {
        "slug": "kaltura",
        "display": "Kaltura",
        "title": "How to Transcribe a Kaltura Video",
        "h1": "How to Transcribe a Kaltura Video",
        "meta_title": "Transcribe Kaltura Video — Enterprise or Campus | TranscriptX",
        "meta_description": "Kaltura's built-in captions cost extra and are slow. If the video has a public share link, paste it on TranscriptX and get the text in minutes.",
        "quick_answer": "Open the Kaltura video → Share → copy the public link. Paste on TranscriptX. If your org requires SSO to view, you'll need the admin to enable public sharing on the specific video, or download it first.",
        "url_example": "https://mediaspace.kaltura.com/media/t/1_abcde12345",
        "steps": [
            {"heading": "Open the video on your Kaltura portal", "body": "Most orgs host Kaltura at <code>mediaspace.ORG.com</code> or a custom subdomain. Open the video page.", "screenshot": None},
            {"heading": "Check the sharing permissions", "body": "Share → Link. If the video is set to \"Anyone\" or \"Anyone with the link,\" you're good. If it's \"Restricted\" or SSO-only, see the breaks section.", "screenshot": None},
            {"heading": "Copy the canonical URL, paste", "body": "The media-entry URL (containing <code>/media/t/</code>) is more reliable than the embed URL. Drop on <a href=\"/\">transcriptx.xyz</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "SSO-locked to your organization", "body": "Kaltura defaults to org-only visibility in most deployments. We can't authenticate. Ask the video owner to switch to Anyone-with-the-link for that video."},
            {"title": "Kaltura Channels with restricted membership", "body": "Some channels are locked to specific user groups. Individual videos inside may still be shareable — get the direct video link, not the channel link."},
            {"title": "Scheduled publishing", "body": "Kaltura lets owners schedule a video to go public later. If it's still in the scheduled window, the URL won't play for us."},
            {"title": "Captions paywalled on your plan", "body": "This is the main reason most Kaltura users come to us — the built-in caption service is a paid per-minute add-on."},
        ],
        "faqs": [
            {"q": "Does the MediaSpace page or the Kaltura Player URL work better?", "a": "MediaSpace page URLs (containing <code>/media/t/</code>) are more reliable. Direct player URLs (containing <code>cdnapi.kaltura.com</code>) sometimes expire or require auth tokens."},
            {"q": "What about Kaltura REACH captions?", "a": "That's Kaltura's own paid captioning. If you already have REACH, you don't need us. If REACH is too slow or too expensive, we're the alternative."},
            {"q": "Can I transcribe multiple Kaltura videos at once?", "a": "Yes, on our batch tier. Paste one URL per line."},
        ],
        "related_slugs": ["transcribe-webinar-for-blog", "transcribe-lecture-for-study-notes"],
    },
    "brightcove": {
        "slug": "brightcove",
        "display": "Brightcove",
        "title": "How to Transcribe a Brightcove Video",
        "h1": "How to Transcribe a Brightcove Video",
        "meta_title": "Transcribe Brightcove Video — Enterprise Video to Text | TranscriptX",
        "meta_description": "Brightcove-hosted videos rarely expose clean captions without a paid add-on. Paste the public URL on TranscriptX and skip the add-on fee.",
        "quick_answer": "If the Brightcove video has a public share URL (not an embed behind a paywall), paste it on TranscriptX. Most public Brightcove content works. Subscription-gated or DRM-protected videos won't.",
        "url_example": "https://players.brightcove.net/ACCOUNTID/PLAYERID_default/index.html?videoId=VIDEOID",
        "steps": [
            {"heading": "Find the video's public URL", "body": "Brightcove videos are usually embedded on a client's website. Right-click the player and copy the source URL, or look for a \"View on Brightcove\" link.", "screenshot": None},
            {"heading": "Confirm it plays publicly", "body": "Open the URL in an incognito window. If it plays for you logged out, we can reach it. If it asks for a login or paywall, we can't.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste → Transcribe.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Embed-only with domain restriction", "body": "Brightcove lets owners restrict playback to specific domains. If the video only plays on certain sites, our servers can't reach it."},
            {"title": "DRM-protected premium video", "body": "Paid streaming services on Brightcove use DRM. Not accessible."},
            {"title": "Token-authenticated URL", "body": "Some enterprise Brightcove setups sign each player request with a token. Those URLs expire quickly and can't be fetched externally."},
            {"title": "Geo-restricted content", "body": "Brightcove is used heavily for licensed sports and news. Geo-restricted content blocks US servers, or non-US if content is US-only."},
        ],
        "faqs": [
            {"q": "What's the simplest way to find a Brightcove video URL on someone's site?", "a": "View the page source, search for <code>players.brightcove.net</code>, and grab the URL. Or use the browser's devtools Network tab to see the manifest URL."},
            {"q": "Does Brightcove's own caption tool do this?", "a": "Brightcove has a paid auto-caption add-on. If you already pay for it, you don't need us. If you don't, we're cheaper for most use cases."},
            {"q": "Can you transcribe a Brightcove video that's behind a corporate SSO?", "a": "No. SSO requires authentication we don't have. Download the video while logged in, then transcribe the file via Drive."},
        ],
        "related_slugs": ["transcribe-webinar-for-blog", "transcribe-sales-call-for-research"],
    },
    "echo360": {
        "slug": "echo360",
        "display": "Echo360",
        "title": "How to Transcribe an Echo360 Lecture",
        "h1": "How to Transcribe an Echo360 Lecture",
        "meta_title": "Transcribe Echo360 Lecture — Campus Video to Text | TranscriptX",
        "meta_description": "Echo360 lectures are usually behind campus SSO. If you can get a public share link, paste it on TranscriptX. Otherwise download first.",
        "quick_answer": "Echo360 lectures default to campus-SSO access. If your instructor has enabled public sharing on the specific lecture, paste the share URL on TranscriptX. If not, your fallback is downloading the recording while logged in and uploading it to Drive.",
        "url_example": "https://echo360.org/lesson/LESSONID/classroom",
        "steps": [
            {"heading": "Open the lecture on Echo360", "body": "Sign in with your campus credentials, open the specific lecture.", "screenshot": None},
            {"heading": "Share → copy public link (if available)", "body": "Click Share on the lecture. If your campus enables it, you'll see an option to generate a public link. Copy that.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste. Lectures are usually 50-90 minutes; transcription takes 2-3 minutes.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Campus SSO required (most common)", "body": "Most Echo360 deployments default to campus-only access. We can't sign in. You'd need the instructor's permission to generate a public link, or download the lecture yourself."},
            {"title": "No public sharing allowed", "body": "Some campuses disable public sharing tenant-wide. Download fallback is the only path."},
            {"title": "Edited sections", "body": "Instructors sometimes edit out discussion or name-drops. Edited gaps transcribe as silence."},
            {"title": "Lecture archived / retired", "body": "Campuses prune old lectures. Past the retention window, the content is gone."},
        ],
        "faqs": [
            {"q": "Echo360 has its own captioning — why use TranscriptX?", "a": "Echo360's caption accuracy is often poor on technical vocabulary. And their export is a restricted text format. We give you clean text, SRT, or VTT."},
            {"q": "What's the download fallback exactly?", "a": "Click Download on the lecture while signed in (if your campus enables it). Upload the resulting .mp4 to Google Drive, share publicly, paste that Drive URL. See <a href=\"/guides/transcribe-google-drive-video\">our Drive guide</a>."},
            {"q": "Can I use this for ALL my semester's lectures?", "a": "If your campus allows public sharing, yes. Our batch tier handles multiple URLs. Worth confirming the sharing policy with the IT admin first."},
        ],
        "related_slugs": ["transcribe-lecture-for-study-notes", "transcribe-google-drive-video", "panopto"],
    },
    "peertube": {
        "slug": "peertube",
        "display": "PeerTube",
        "title": "How to Transcribe a PeerTube Video",
        "h1": "How to Transcribe a PeerTube Video",
        "meta_title": "Transcribe PeerTube Video — Federated Video to Text | TranscriptX",
        "meta_description": "PeerTube is federated, so URLs vary by instance. Copy the canonical video URL on its home instance and paste on TranscriptX.",
        "quick_answer": "PeerTube runs as many independent instances. Copy the URL from the video's home instance (the server where it was originally uploaded) and paste on TranscriptX. Videos mirrored on other instances may work too, but the canonical home-instance URL is most reliable.",
        "url_example": "https://instance-name.org/w/VIDEOID",
        "steps": [
            {"heading": "Find the home instance", "body": "If you're watching on a mirror, look for a \"View on original instance\" link. The home instance is the one where the video was actually uploaded.", "screenshot": None},
            {"heading": "Copy the canonical URL", "body": "PeerTube URL format is <code>instance.tld/w/VIDEO_UUID</code>. Copy that from the browser.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Instance down or federating poorly", "body": "Smaller PeerTube instances go down regularly. If the home instance is unreachable, try a mirror. If no mirror, wait for it to come back."},
            {"title": "Instance-specific access rules", "body": "Each instance sets its own rules. Some require login even for public videos. If the video plays logged-out in a browser, it plays for us."},
            {"title": "Rate-limited instance", "body": "Some PeerTube admins aggressively rate-limit external scrapers. Our servers may get temporarily blocked — try again in an hour."},
            {"title": "Video redistributed from another federated service", "body": "PeerTube bridges exist (e.g., YouTube mirror instances). The rebroadcast quality is often lower — find the original if you can."},
        ],
        "faqs": [
            {"q": "Why is PeerTube video harder than YouTube?", "a": "PeerTube is federated — no single company to work with. Each instance has its own policies, uptime, and quirks. The paste-a-URL flow mostly works, but the edge cases are more varied."},
            {"q": "Does this work for LBRY/Odysee?", "a": "LBRY/Odysee are different — different protocol. See our <a href=\"/how-to-transcribe/odysee\">Odysee guide</a>."},
            {"q": "Can I transcribe PeerTube videos that are set to unlisted?", "a": "Yes, if you have the direct link. Unlisted on PeerTube means \"not in search\" but reachable by URL — same as unlisted YouTube."},
        ],
        "related_slugs": ["transcribe-private-youtube-video", "transcribe-foreign-language-video"],
    },
    "odysee": {
        "slug": "odysee",
        "display": "Odysee / LBRY",
        "title": "How to Transcribe an Odysee / LBRY Video",
        "h1": "How to Transcribe an Odysee / LBRY Video",
        "meta_title": "Transcribe Odysee Video — LBRY Blockchain Video to Text | TranscriptX",
        "meta_description": "Odysee videos live on the LBRY blockchain. Copy the odysee.com URL and paste on TranscriptX — same paste-and-go as YouTube.",
        "quick_answer": "Copy the Odysee URL from your browser (odysee.com/@Channel/video-title:UUID), paste on TranscriptX. Works for public Odysee content. Livestreams need to end first; creator-only or paywalled videos don't work.",
        "url_example": "https://odysee.com/@Channel:x/Video-Title:abc12",
        "steps": [
            {"heading": "Open the Odysee video", "body": "On odysee.com, click the video. Copy the URL from the browser.", "screenshot": None},
            {"heading": "URL format", "body": "Odysee URLs look like <code>odysee.com/@Channel:x/Video-Title:abc12</code>. The colons are important — keep them.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Drop on <a href=\"/\">transcriptx.xyz</a>. Long videos (Odysee has fewer length restrictions than YouTube) take proportionally longer.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Creator-only / tipped access", "body": "Some Odysee creators gate content behind tipping or membership. Those aren't accessible to us."},
            {"title": "Livestream in progress", "body": "Wait for the stream to end. Odysee saves streams to the channel after; that saved version works."},
            {"title": "Content removed from Odysee's frontend", "body": "Rare, but Odysee occasionally removes content from their frontend. The underlying LBRY data may still exist but we can't reach it via the blocked URL."},
            {"title": "LBRY Desktop URLs", "body": "Some users share <code>lbry://</code> protocol URLs. We can't open those. Ask for the odysee.com HTTPS URL instead."},
        ],
        "faqs": [
            {"q": "What's the difference between Odysee and LBRY?", "a": "LBRY is the underlying blockchain protocol; Odysee is the most popular web frontend for it. For transcription, use odysee.com URLs — we can't open <code>lbry://</code> protocol URLs."},
            {"q": "Are Odysee videos monetized differently?", "a": "Yes (LBC tokens / tips), but that doesn't affect transcription. Public videos are transcribable regardless of whether they have tip buttons."},
            {"q": "What about censorship — are Odysee videos more likely to disappear?", "a": "Odysee is less aggressive about removals than YouTube, but they do remove some content. If a URL 404s, we can't recover it."},
        ],
        "related_slugs": ["peertube", "transcribe-private-youtube-video"],
    },
    "zoom-webinar": {
        "slug": "zoom-webinar",
        "display": "Zoom Webinar",
        "title": "How to Transcribe a Zoom Webinar Recording",
        "h1": "How to Transcribe a Zoom Webinar Recording",
        "meta_title": "Transcribe Zoom Webinar Recording — Paste the Link | TranscriptX",
        "meta_description": "Zoom Webinars save recordings just like meetings. Share the cloud link publicly, paste it on TranscriptX, get the transcript for your blog post or report.",
        "quick_answer": "Zoom Webinar cloud recordings work the same as meeting recordings — go to zoom.us → Recordings, open the webinar, share publicly (no passcode), copy the link, paste on TranscriptX. Registration-locked replays need the passcode removed.",
        "url_example": "https://zoom.us/rec/share/ABC123_longHash",
        "steps": [
            {"heading": "Go to zoom.us → Recordings", "body": "Sign in as the webinar host. Click <strong>Recordings</strong>, find the webinar by date.", "screenshot": None},
            {"heading": "Share publicly, remove passcode", "body": "Click Share. Turn on <strong>Publicly</strong>. Turn off <strong>Passcode Protection</strong>. Copy the link.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "Webinars run longer than meetings — 60-90 minutes is typical. Transcription takes a few minutes for long ones. Drop the link on <a href=\"/\">transcriptx.xyz</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Passcode on the share link", "body": "We can't type passcodes. Remove passcode protection on the specific webinar recording."},
            {"title": "Registration required on the recording", "body": "Zoom lets you gate replays behind registration. Our servers can't fill out a registration form."},
            {"title": "Webinar report wanted instead of transcript", "body": "Zoom's webinar report (attendee list, Q&A log) is a different product. We only transcribe the audio."},
            {"title": "Recording auto-deleted", "body": "Free Zoom plans expire cloud recordings quickly. Download locally before the retention window closes."},
        ],
        "faqs": [
            {"q": "Why is this a separate guide from the regular Zoom recording one?", "a": "Webinars have distinct features (registration, Q&A panels, panelist vs attendee roles) that cause different failure modes. The core paste-and-go flow is similar."},
            {"q": "Can I transcribe while the webinar is live?", "a": "No. Live captioning is a different product. Wait for the recording."},
            {"q": "What about the in-webinar chat / Q&A log?", "a": "Those export as separate files from Zoom's reports panel. We only process the audio recording."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-webinar-for-blog"],
    },
    "google-meet": {
        "slug": "google-meet",
        "display": "Google Meet",
        "title": "How to Transcribe a Google Meet Recording",
        "h1": "How to Transcribe a Google Meet Recording",
        "meta_title": "Transcribe Google Meet Recording — Meeting to Text | TranscriptX",
        "meta_description": "Google Meet saves recordings to Drive. Open the Drive file, share publicly, paste the URL on TranscriptX. Works on any Workspace plan that enables recording.",
        "quick_answer": "Google Meet recordings save to the meeting organizer's Google Drive in a \"Meet Recordings\" folder. Open the .mp4 in Drive, Share → Anyone with the link → copy URL → paste on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Find the recording in Drive", "body": "Open Google Drive (drive.google.com) → <strong>Meet Recordings</strong> folder. Recordings are named by the meeting date.", "screenshot": None},
            {"heading": "Share publicly", "body": "Right-click the .mp4 → Share → switch access from Restricted to <strong>Anyone with the link</strong>. Copy link.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste. Multi-hour meetings take a few minutes to process.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Recording was never saved", "body": "Meet only records when the host clicks the record button (or meets specific admin-set conditions). If nobody hit record, there's no file to transcribe."},
            {"title": "Admin disabled external sharing", "body": "Workspace admins can force \"people in your org only\" on shared links. Download the file locally, upload to personal Drive, share from there."},
            {"title": "Free personal accounts can't record Meet", "body": "Recording is a Workspace feature. Personal gmail accounts can't record a Meet call at all."},
            {"title": "Recording still processing", "body": "After a meeting ends, Google takes minutes to hours to transcode the recording and place it in Drive. If it's not there yet, wait."},
        ],
        "faqs": [
            {"q": "Doesn't Meet have its own transcription?", "a": "On some Workspace tiers, yes — it saves a Doc in the Meet Recordings folder. But the Doc is often low-quality and doesn't export cleanly. We give you better text from the audio."},
            {"q": "What about Meet captions (the real-time kind)?", "a": "Live captions aren't saved by default. Only the audio recording is. We transcribe the audio."},
            {"q": "Can I transcribe a meeting I wasn't the host of?", "a": "Only if the host shares the recording with you. Once they give you a shareable Drive link, the flow is the same."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-google-drive-video", "transcribe-microsoft-teams-recording"],
    },
    "webex": {
        "slug": "webex",
        "display": "Cisco WebEx",
        "title": "How to Transcribe a Cisco WebEx Recording",
        "h1": "How to Transcribe a Cisco WebEx Recording",
        "meta_title": "Transcribe Cisco WebEx Recording — Meeting or Webinar to Text | TranscriptX",
        "meta_description": "WebEx recordings are stored in the WebEx cloud or downloaded locally. Share publicly or upload to Drive, then paste on TranscriptX.",
        "quick_answer": "If your WebEx recording has a public share link, paste it on TranscriptX. If your org restricts sharing, download the MP4 from WebEx, upload to Google Drive with Anyone-with-the-link, paste the Drive URL.",
        "url_example": "https://company.webex.com/recordingservice/sites/company/recording/playback/RECORDINGID",
        "steps": [
            {"heading": "Open WebEx recordings", "body": "Sign in at <code>yourcompany.webex.com</code>. Go to Recordings.", "screenshot": None},
            {"heading": "Get a shareable link", "body": "Click the recording → Share. Set access to <strong>Public / External</strong> if your admin allows. Remove passwords.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "If sharing is disabled, use the Drive fallback — download the MP4, upload to Drive, share from there. See <a href=\"/guides/transcribe-google-drive-video\">Drive guide</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Corporate site blocks external sharing", "body": "Most enterprise WebEx deployments disable external sharing by default. Download-then-upload-to-Drive is the reliable workaround."},
            {"title": "Password-protected recording", "body": "We can't type passwords. Remove the password on the recording, or use the Drive fallback."},
            {"title": "Recording expired", "body": "WebEx recordings have retention limits per site. Past the window, they're gone."},
            {"title": "MP4 download requires desktop app", "body": "Some WebEx sites only let you download recordings through the WebEx desktop client, not the browser. You'll need to install the client to grab the file."},
        ],
        "faqs": [
            {"q": "Does WebEx have its own transcription?", "a": "Yes, as part of some WebEx Assistant tiers. If you already have it and it's good enough, you don't need us. If it's not or you don't, we're the alternative."},
            {"q": "Why does my IT block external sharing?", "a": "Standard security policy — enterprise meetings often contain sensitive info. Respect the policy. The download-and-upload-to-personal-Drive path is how people usually work around it for personal productivity needs."},
            {"q": "Any difference between WebEx Meetings and WebEx Events?", "a": "For transcription, no. Both produce an MP4 recording. The URL patterns differ slightly but the paste flow is identical."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-google-drive-video", "transcribe-microsoft-teams-recording"],
    },
    "gotomeeting": {
        "slug": "gotomeeting",
        "display": "GoToMeeting",
        "title": "How to Transcribe a GoToMeeting Recording",
        "h1": "How to Transcribe a GoToMeeting Recording",
        "meta_title": "Transcribe GoToMeeting Recording — Meeting to Text | TranscriptX",
        "meta_description": "GoToMeeting / GoTo recordings save locally or to the cloud. Upload to Drive or use the share link, then paste on TranscriptX.",
        "quick_answer": "GoToMeeting (now GoTo) recordings are usually saved either locally on the organizer's computer or in the GoTo cloud. For local recordings, upload the .mp4 to Google Drive and share publicly. For cloud recordings, copy the public share link from the Meetings Hub.",
        "url_example": "https://meet.goto.com/recording/RECORDINGID",
        "steps": [
            {"heading": "Locate the recording", "body": "Cloud recording: sign in at <code>meet.goto.com</code> → Meetings Hub → Recordings. Local recording: find the .mp4 on the organizer's computer (usually in Documents folder).", "screenshot": None},
            {"heading": "Get a shareable link", "body": "Cloud: click Share on the recording, make it public, copy link. Local: upload the .mp4 to <a href=\"/guides/transcribe-google-drive-video\">Google Drive</a> with Anyone-with-the-link.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Recording was saved locally, not to cloud", "body": "GoToMeeting's default on many plans is local recording. That file is on the organizer's machine only. Upload-to-Drive is the workaround."},
            {"title": "Admin restricts external sharing on cloud recordings", "body": "Enterprise tiers sometimes block public share links. Download + Drive fallback is the answer."},
            {"title": "Old-format recordings", "body": "GoToMeeting used to save recordings in a proprietary <code>.g2m</code> format. Those need to be converted to .mp4 first (GoTo's own converter does this)."},
            {"title": "Product renamed — URLs changed", "body": "GoToMeeting became GoTo; older meet.logmeininc.com URLs redirect but sometimes break. Grab a fresh link from the new GoTo portal if old ones 404."},
        ],
        "faqs": [
            {"q": "Is GoToMeeting the same as GoToWebinar?", "a": "Related products from the same company, both now branded GoTo. Recording flow is similar; webinars tend to have longer retention and more-gated sharing defaults."},
            {"q": "What about the old .g2m files people have lying around?", "a": "Use GoTo's own converter to turn them into .mp4. Then upload to Drive and transcribe."},
            {"q": "Does this work for GoToTraining?", "a": "Yes. Same recording format, same share flow. Different product, same transcription path."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-webinar-for-blog", "transcribe-google-drive-video"],
    },
    "microsoft-stream": {
        "slug": "microsoft-stream",
        "display": "Microsoft Stream",
        "title": "How to Transcribe a Microsoft Stream Video",
        "h1": "How to Transcribe a Microsoft Stream Video",
        "meta_title": "Transcribe Microsoft Stream Video — SharePoint-Hosted Video to Text | TranscriptX",
        "meta_description": "New Microsoft Stream stores videos in SharePoint / OneDrive. Share the video externally, paste the URL on TranscriptX.",
        "quick_answer": "The new Microsoft Stream (Stream on SharePoint) is just SharePoint video. Open the video in SharePoint or OneDrive, Share → Anyone with the link, paste on TranscriptX. If your tenant forces domain-only sharing, use the Drive fallback.",
        "url_example": "https://tenant.sharepoint.com/personal/user/_layouts/15/stream.aspx?id=VIDEOID",
        "steps": [
            {"heading": "Find the video in SharePoint / OneDrive", "body": "Microsoft Stream (on SharePoint) videos live in SharePoint document libraries or OneDrive. Find the .mp4 by the usual Microsoft navigation.", "screenshot": None},
            {"heading": "Share with Anyone-with-the-link", "body": "Click Share. If your tenant allows it, switch access from People-in-your-organization to <strong>Anyone with the link</strong>. Copy the URL.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Tenant blocks external sharing", "body": "Most common issue. Your SharePoint admin has disabled external sharing tenant-wide. Download the .mp4 locally, upload to personal Drive, share from there."},
            {"title": "Classic Stream (pre-2024) URLs", "body": "Microsoft retired Classic Stream. Those microsoftstream.com URLs should all redirect to SharePoint now. If you have very old links, they might just be dead."},
            {"title": "Video moved after share link was generated", "body": "Moving a file in SharePoint can invalidate the share link. Grab a fresh one."},
            {"title": "Labeled / sensitivity-classified content", "body": "Purview sensitivity labels block sharing of some enterprise videos entirely. Talk to IT — no external tool can transcribe sealed content."},
        ],
        "faqs": [
            {"q": "What's the difference between Classic Stream and new Stream?", "a": "Classic Stream (microsoftstream.com) was retired. New Stream is just SharePoint video with a Stream-branded player. For transcription, treat it like SharePoint video."},
            {"q": "Does this handle Teams meeting recordings too?", "a": "Teams recordings save to OneDrive for 1:1s and SharePoint for channels — same underlying platform. See our <a href=\"/guides/transcribe-microsoft-teams-recording\">Teams guide</a> for the Teams-specific flow."},
            {"q": "My org uses Purview labels — will they affect transcription?", "a": "Depends on the label. Confidential labels often block external sharing, which blocks us. Internal labels usually don't affect share link flows."},
        ],
        "related_slugs": ["transcribe-microsoft-teams-recording", "transcribe-google-drive-video"],
    },
    "dropbox-video": {
        "slug": "dropbox-video",
        "display": "Dropbox",
        "title": "How to Transcribe a Video Stored in Dropbox",
        "h1": "How to Transcribe a Video Stored in Dropbox",
        "meta_title": "Transcribe Dropbox Video — Share Link to Text | TranscriptX",
        "meta_description": "If your video lives in Dropbox, get a public share link and paste it on TranscriptX. Same paste-and-go flow as Google Drive, different sharing UI.",
        "quick_answer": "Right-click the video in Dropbox → <strong>Copy link</strong>. Paste on TranscriptX. The default Dropbox link is \"Anyone with the link can view\" which is what we need. Team folders with restricted sharing need admin permission to share externally.",
        "url_example": "https://www.dropbox.com/s/abc123xyz/video.mp4?dl=0",
        "steps": [
            {"heading": "Right-click the video in Dropbox", "body": "On dropbox.com or the desktop client, right-click the .mp4 → <strong>Copy link</strong>. Dropbox generates a share URL automatically.", "screenshot": None},
            {"heading": "Verify it's \"Anyone with the link\"", "body": "Click <strong>Share</strong> on the file to confirm. Team folders default to org-only; personal folders default to anyone-with-link.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste. Dropbox's <code>?dl=0</code> in the URL is fine; we strip it.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Team folder with restricted sharing", "body": "Dropbox Business team folders can lock external sharing. Ask your admin, or move the file to your personal Dropbox first."},
            {"title": "Password-protected link", "body": "Paid Dropbox plans let you password-protect share links. We can't type the password — remove it temporarily."},
            {"title": "Expiring share link", "body": "Business plans can set link expirations. If the link worked yesterday and doesn't today, the expiration passed."},
            {"title": "Dropbox Transfer (not Dropbox Share)", "body": "Dropbox Transfer links are a different product — usually time-limited and single-download. Paste them and they might work once; better to use a regular Share link."},
        ],
        "faqs": [
            {"q": "Do I need a paid Dropbox account for this to work?", "a": "No. Free Dropbox's default \"Anyone with the link\" sharing works fine for us. Paid features (passwords, expiration) add complications, not capabilities."},
            {"q": "What about huge files — 10+ GB?", "a": "Dropbox's large-file uploads work. On our side, transcription time scales with duration, not file size. A 3-hour video is a 3-hour video whether it's 1GB or 10GB."},
            {"q": "Does it work with Dropbox-hosted audio files (.mp3, .m4a)?", "a": "Yes. Any audio or video Dropbox stores and shares publicly is transcribable."},
        ],
        "related_slugs": ["transcribe-google-drive-video", "transcribe-iphone-video"],
    },
    "onedrive-video": {
        "slug": "onedrive-video",
        "display": "OneDrive (personal)",
        "title": "How to Transcribe a Personal OneDrive Video",
        "h1": "How to Transcribe a Personal OneDrive Video",
        "meta_title": "Transcribe OneDrive Video — Personal File to Text | TranscriptX",
        "meta_description": "Personal OneDrive videos (not Teams, not SharePoint) have a cleaner share flow. Get the Anyone-with-the-link URL, paste on TranscriptX.",
        "quick_answer": "Right-click the video in OneDrive → Share → change access to <strong>Anyone with the link</strong> → Copy link. Paste on TranscriptX. For Teams-recording OneDrive files, see the Teams guide — different folder, similar flow.",
        "url_example": "https://onedrive.live.com/?cid=ABC&id=DEF%21123",
        "steps": [
            {"heading": "Right-click the video in OneDrive", "body": "On onedrive.live.com (personal) or office.com/onedrive (work), right-click the .mp4 → Share.", "screenshot": None},
            {"heading": "Change to Anyone with the link", "body": "Default for work/school OneDrive is \"People in your organization.\" Switch to <strong>Anyone with the link</strong>. Personal OneDrive defaults to Anyone-with-the-link already.", "screenshot": None},
            {"heading": "Copy link, paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste → Transcribe.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Work OneDrive with external sharing disabled", "body": "Same story as SharePoint — admin policy blocks external sharing. Download to laptop, re-upload to personal Drive or Dropbox, share from there."},
            {"title": "Password on the share link", "body": "Work/school OneDrive can add passwords. We can't type them. Remove or use Drive fallback."},
            {"title": "Expiring access", "body": "Admins can set share-link expiration. Check with the file owner if a previously-working link stops."},
            {"title": "Personal vs work OneDrive URL differences", "body": "Personal: <code>onedrive.live.com/...</code>. Work: <code>tenant-my.sharepoint.com/personal/...</code>. Both work, but they behave under different admin policies."},
        ],
        "faqs": [
            {"q": "Why is personal OneDrive different from the Teams/SharePoint flow?", "a": "Personal OneDrive has looser defaults and fewer admin controls. Work/school OneDrive is basically SharePoint under the hood — gated by your tenant's policies."},
            {"q": "What about OneDrive mobile?", "a": "Same Share flow, different UI. Tap the file → Share → change access to Anyone-with-link, copy."},
            {"q": "Is there a free-tier issue?", "a": "Free OneDrive gives you 5GB. If you're over quota, sharing might fail in weird ways. Check Drive status first."},
        ],
        "related_slugs": ["transcribe-microsoft-teams-recording", "transcribe-google-drive-video", "microsoft-stream"],
    },
    "patreon-video": {
        "slug": "patreon-video",
        "display": "Patreon",
        "title": "How to Transcribe a Patreon Video (The Honest Version)",
        "h1": "How to Transcribe a Patreon Video",
        "meta_title": "Transcribe Patreon Video — Supporter-Only Content | TranscriptX",
        "meta_description": "Patreon content is behind a paywall. No external tool can transcribe supporter-only posts without being logged in. Here's what actually works.",
        "quick_answer": "Public Patreon posts (the free ones creators share to promote their paid tier) work — paste the URL. Supporter-only posts require your own authenticated Patreon session; external tools can't fetch them. Download the video from your Patreon account while logged in, upload to Drive, transcribe that.",
        "url_example": "https://www.patreon.com/posts/post-title-123456789",
        "steps": [
            {"heading": "Check if the post is public", "body": "Open the Patreon post in an incognito window. If it plays without login, we can reach it. If it asks for login or tier membership, we can't.", "screenshot": None},
            {"heading": "For public posts — just paste", "body": "Copy the post URL, drop on <a href=\"/\">transcriptx.xyz</a>.", "screenshot": None},
            {"heading": "For supporter-only posts — download first", "body": "Sign in to Patreon. Download the video from the post (creators usually enable downloads for supporters). Upload to <a href=\"/guides/transcribe-google-drive-video\">Google Drive</a>, share publicly, paste that Drive link.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Supporter-only content", "body": "The whole point of Patreon is paywalled content. External transcription without auth is impossible by design. Download workflow is the only path."},
            {"title": "Creator disabled downloads", "body": "Some creators disable downloads to prevent piracy. You can't easily extract the video. Ask the creator, or be okay with it being inaccessible."},
            {"title": "Post deleted or removed", "body": "Creators delete posts regularly. If gone, it's gone."},
            {"title": "Patreon removed for TOS reasons", "body": "Rare but happens. Creator moved to another platform. Look for the content there."},
        ],
        "faqs": [
            {"q": "Is this ethical if I'm a paid supporter?", "a": "Transcribing a video you paid to access, for your own personal use (study, notes, accessibility), is generally fine. Republishing the transcript publicly is a copyright question — ask the creator before you post."},
            {"q": "What about Patreon's RSS feed for audio posts?", "a": "Supporters get personalized RSS feeds for audio. The URLs are signed to your account and shouldn't be shared. You could paste one into TranscriptX from the same browser session, but be aware the URL embeds your access token."},
            {"q": "Can I transcribe Patreon comments or community posts?", "a": "Comments are text — you don't need transcription. Community-post videos follow the same rule as regular posts (public vs supporter-only)."},
        ],
        "related_slugs": ["transcribe-google-drive-video", "transcribe-mp3-from-url"],
    },
    "substack-audio": {
        "slug": "substack-audio",
        "display": "Substack (audio / podcast)",
        "title": "How to Transcribe a Substack Podcast or Audio Post",
        "h1": "How to Transcribe a Substack Podcast or Audio Post",
        "meta_title": "Transcribe Substack Podcast — Free or Paid Audio Post | TranscriptX",
        "meta_description": "Substack audio posts come in free and paid tiers. Free posts paste directly. Paid posts need a download-from-your-account workflow.",
        "quick_answer": "Public Substack audio posts: copy the post URL, paste on TranscriptX. Paid subscriber-only posts: download the MP3 from your logged-in Substack, upload to Drive, paste that Drive link.",
        "url_example": "https://writer.substack.com/p/post-slug",
        "steps": [
            {"heading": "Check if the post is public", "body": "Open the post in an incognito window. If the audio plays fully, it's public. If you get a paywall cutting off after a sample, it's paid-only.", "screenshot": None},
            {"heading": "For public posts", "body": "Copy the post URL (<code>writer.substack.com/p/slug</code>). Paste on <a href=\"/\">transcriptx.xyz</a>.", "screenshot": None},
            {"heading": "For paid posts", "body": "Sign in, download the MP3 (most Substack audio posts offer download for subscribers). Upload to Drive with Anyone-with-link, paste the Drive URL.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Paid subscriber-only posts", "body": "Paywall, same as Patreon. Download while logged in, re-upload to Drive for our flow."},
            {"title": "\"Full subscriber only\" comments sections", "body": "Substack has tiered paywalls — some posts are free to read but paid to hear audio. Listen-check in incognito before trying to paste."},
            {"title": "Substack removed the post", "body": "Writers sometimes remove posts. If gone, it's gone."},
            {"title": "Podcast RSS feed with per-subscriber token", "body": "Substack's paid-podcast RSS feeds embed your account token. Technically transcribable, but be aware the URL leaks your subscription."},
        ],
        "faqs": [
            {"q": "Why not just use the Substack app's own transcript feature?", "a": "Substack has started adding auto-transcripts for some podcasts, but quality varies and exports are limited. We give you clean text, SRT, or VTT from the actual audio."},
            {"q": "What's the difference between this and the generic MP3-URL guide?", "a": "If you have a direct .mp3 URL from a Substack post, the generic <a href=\"/guides/transcribe-mp3-from-url\">MP3 guide</a> works too. This guide covers the post URL path."},
            {"q": "Can I transcribe paid Substack content my friend shared?", "a": "Only if your friend shared the actual audio file. Shared links usually still require subscription."},
        ],
        "related_slugs": ["transcribe-mp3-from-url", "transcribe-spotify-podcast"],
    },
    "bandcamp": {
        "slug": "bandcamp",
        "display": "Bandcamp",
        "title": "How to Transcribe a Bandcamp Audio Post or Podcast",
        "h1": "How to Transcribe a Bandcamp Audio",
        "meta_title": "Transcribe Bandcamp Audio — Music or Podcast to Text | TranscriptX",
        "meta_description": "Bandcamp hosts music and some podcast/spoken-word content. For anything public, paste the track URL. Paid-only tracks need a purchase-then-download flow.",
        "quick_answer": "Public Bandcamp tracks: copy the track URL, paste on TranscriptX. Purchase-only tracks: buy, download the MP3, upload to Drive, paste. Useful mainly for spoken-word: audiobooks, DJ-set voice-overs, interview podcasts hosted on Bandcamp.",
        "url_example": "https://artist.bandcamp.com/track/track-name",
        "steps": [
            {"heading": "Open the track on Bandcamp", "body": "On artist.bandcamp.com, open the specific track (not the album page). The URL will include <code>/track/</code>.", "screenshot": None},
            {"heading": "Verify it's publicly streamable", "body": "Bandcamp lets artists offer free streaming or preview-only. Listen-check in an incognito window.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste. Note: Whisper is tuned for speech. Songs with lyrics produce rough transcripts; pure instrumentals produce nothing.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Preview-only streaming", "body": "Artists can limit free streaming to a short preview. We only get the preview's audio — the full track needs purchase."},
            {"title": "Paid-only downloads", "body": "Pay-what-you-want tracks with a minimum price can't be streamed in full for free. Purchase and download before transcribing."},
            {"title": "Music content (non-spoken)", "body": "Bandcamp is mostly music. Lyrics transcribe poorly; instrumentals not at all. Most useful for spoken-word content (audiobooks, podcast-style releases)."},
            {"title": "Album URL vs track URL", "body": "Album URLs play all tracks sequentially. We transcribe a single track — use the individual track URL, not the album URL."},
        ],
        "faqs": [
            {"q": "Is this actually a common use case?", "a": "Niche but real — audiobook publishers on Bandcamp, podcasts sold as \"pay what you want\", and spoken-word artists all need transcripts. DJ mixes with crowd voice-over occasionally transcribe usefully."},
            {"q": "Does this handle Bandcamp Daily articles?", "a": "Those are written articles, not audio. No transcription needed."},
            {"q": "What about Bandcamp Radio / Bandcamp Weekly?", "a": "Public episodes work when streamable. Grab the episode URL from bandcamp.com/?show= or the individual radio archive."},
        ],
        "related_slugs": ["transcribe-soundcloud-track", "transcribe-mp3-from-url"],
    },
    "apple-podcasts": {
        "slug": "apple-podcasts",
        "display": "Apple Podcasts",
        "title": "How to Transcribe an Apple Podcasts Episode",
        "h1": "How to Transcribe an Apple Podcasts Episode",
        "meta_title": "Transcribe Apple Podcasts Episode — Find the MP3, Paste | TranscriptX",
        "meta_description": "Apple Podcasts itself doesn't give you a direct audio URL, but the underlying RSS feed does. Here's how to find and paste the MP3.",
        "quick_answer": "Apple Podcasts is a directory — the actual MP3 lives on the show's own host. Find the episode on the show's website or its RSS feed, grab the direct MP3 URL, paste on TranscriptX. Apple Podcasts Subscription (paid) episodes need to be downloaded from your logged-in Apple device first.",
        "url_example": "https://traffic.libsyn.com/showname/episode-123.mp3",
        "steps": [
            {"heading": "Find the podcast's RSS feed", "body": "Every public podcast has an RSS URL. On Apple Podcasts web, click the show → scroll to the bottom — sometimes the RSS URL is listed. Or use <a href=\"https://castos.com/tools/find-podcast-rss-feed/\" rel=\"nofollow\">a podcast RSS finder</a>.", "screenshot": None},
            {"heading": "Grab the episode's MP3 URL from the feed", "body": "Open the RSS URL in a browser. For the episode you want, find the <code>&lt;enclosure url=\"...\"&gt;</code> — that's the direct MP3 URL.", "screenshot": None},
            {"heading": "Paste the MP3 URL on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste the MP3 URL.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Apple Podcasts Subscription (paid)", "body": "Paid Apple Podcast Subscription shows distribute via Apple-authenticated URLs that external tools can't reach. Download in your podcast app, upload to Drive."},
            {"title": "Show pulled from Apple but still running elsewhere", "body": "Apple removes shows sometimes. Check the show's own website — they'll usually still distribute via RSS even after delisting."},
            {"title": "Private RSS feed", "body": "Some premium shows (Patreon, Supercast, etc.) give subscribers private RSS URLs with auth tokens embedded. Those work with us technically, but be cautious about leaking the token."},
            {"title": "Dynamic ad insertion", "body": "Podcast ads get stitched in at fetch time. Your transcript will include whatever ads ran when we grabbed the file."},
        ],
        "faqs": [
            {"q": "Why can't I just use the Apple Podcasts URL directly?", "a": "Apple Podcasts URLs (<code>podcasts.apple.com/...</code>) are web pages, not audio files. They direct users to Apple's app. We need the actual MP3 that the episode is backed by."},
            {"q": "What's the easiest way to find the RSS feed?", "a": "Search for the show's own website — most have \"Subscribe\" buttons that list the feed URL. Or use <a href=\"https://castos.com/tools/find-podcast-rss-feed/\" rel=\"nofollow\">Castos' RSS finder</a>."},
            {"q": "Does this work for Stitcher / other aggregators too?", "a": "Yes, same principle — the aggregator shows the episode, but the MP3 is hosted on the show's own host. Find the RSS, grab the MP3."},
        ],
        "related_slugs": ["transcribe-mp3-from-url", "transcribe-spotify-podcast"],
    },
    "anchor-spotify-podcasters": {
        "slug": "anchor-spotify-podcasters",
        "display": "Anchor / Spotify for Podcasters",
        "title": "How to Transcribe an Anchor or Spotify-for-Podcasters Episode",
        "h1": "How to Transcribe an Anchor / Spotify for Podcasters Episode",
        "meta_title": "Transcribe Anchor Podcast — Spotify for Podcasters Episodes | TranscriptX",
        "meta_description": "Anchor (now Spotify for Podcasters) still distributes via RSS even for Spotify-exclusive content. Here's how to get a transcribable URL.",
        "quick_answer": "Spotify for Podcasters (formerly Anchor) shows usually still have a public RSS feed even if the show feels \"Spotify-native.\" Find the RSS, grab the episode MP3, paste on TranscriptX. Spotify-exclusive shows with no RSS can't be reached externally — transcribe via the RSS-supported backup episode page.",
        "url_example": "https://anchor.fm/s/SHOWID/podcast/rss",
        "steps": [
            {"heading": "Find the show's RSS feed", "body": "Go to the show's page on anchor.fm or podcasters.spotify.com. The RSS URL is at <code>anchor.fm/s/SHOWID/podcast/rss</code> — you can find it in the page source or via the show's \"Distribute to\" settings.", "screenshot": None},
            {"heading": "Find the episode's MP3 in the RSS", "body": "Open the RSS URL, locate the episode by title, copy the <code>&lt;enclosure url=\"...\"&gt;</code> value.", "screenshot": None},
            {"heading": "Paste the MP3 URL on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Spotify-exclusive show with no RSS", "body": "Truly Spotify-exclusive shows turn off RSS syndication. Those aren't reachable externally — you'd need to download from Spotify on your account (not a smooth path)."},
            {"title": "Monetized episodes with ad-break markers", "body": "Dynamic ad insertion at fetch time means transcripts include whatever ads were served. Fine for your own use; don't republish with the ads."},
            {"title": "Anchor \"background music\" feature", "body": "Anchor lets creators add background music, which sometimes lowers transcription accuracy. Use the language retry if Whisper mis-detects speech for music."},
            {"title": "Legacy anchor.fm vs new podcasters.spotify.com URLs", "body": "Spotify renamed Anchor but old anchor.fm URLs usually redirect. If they don't, find the new podcasters.spotify.com equivalent."},
        ],
        "faqs": [
            {"q": "Is Anchor the same as Spotify for Podcasters now?", "a": "Yes. Spotify rebranded Anchor to Spotify for Podcasters in 2023. Same product, new URL scheme."},
            {"q": "Why not just use Spotify's own podcast transcription?", "a": "Spotify has added transcription for some podcasts, but coverage is inconsistent and exports aren't supported. We give you the text in a format you can actually use."},
            {"q": "What about videos on Spotify podcasts (the video podcast format)?", "a": "Video podcasts on Spotify distribute the audio track normally via RSS. Transcribe the audio the same way. The video portion requires you to be a Spotify-app user to view."},
        ],
        "related_slugs": ["transcribe-spotify-podcast", "transcribe-mp3-from-url", "apple-podcasts"],
    },
    "buzzsprout": {
        "slug": "buzzsprout",
        "display": "Buzzsprout",
        "title": "How to Transcribe a Buzzsprout-Hosted Podcast Episode",
        "h1": "How to Transcribe a Buzzsprout-Hosted Podcast Episode",
        "meta_title": "Transcribe Buzzsprout Podcast — Direct MP3 or Episode Page | TranscriptX",
        "meta_description": "Buzzsprout exposes the direct MP3 on its public episode pages. Copy the episode URL (or the direct MP3 link from its RSS feed) and paste on TranscriptX.",
        "quick_answer": "Open the Buzzsprout episode page. Right-click the audio player and copy the audio source URL, or grab the show's RSS feed to get the direct MP3. Paste on TranscriptX.",
        "url_example": "https://www.buzzsprout.com/SHOWID/episodes/EPISODEID.mp3",
        "steps": [
            {"heading": "Open the Buzzsprout episode page", "body": "Podcast's show page on Buzzsprout lists episodes with a built-in player.", "screenshot": None},
            {"heading": "Get the direct MP3 URL", "body": "Right-click the audio player → Copy audio URL. Format will be <code>buzzsprout.com/SHOWID/episodes/EPISODEID.mp3</code>. Or grab it from the show's RSS.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste the MP3 URL.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Private / unlisted episodes", "body": "Buzzsprout lets shows mark episodes private. Those don't appear on public feeds. The host has to publicize them first."},
            {"title": "Advanced-plan \"Magic Mastering\" effects", "body": "Doesn't affect transcription — just flagging it exists. Transcription accuracy is unchanged."},
            {"title": "Direct MP3 link expires", "body": "Buzzsprout sometimes rotates direct MP3 URLs. If a link stops working, grab a fresh one from the RSS feed."},
            {"title": "Dynamic ad insertion", "body": "Same as any modern podcast host — ads get stitched in at fetch time and appear in the transcript."},
        ],
        "faqs": [
            {"q": "Is this the same flow as other podcast hosts (Libsyn, Podbean)?", "a": "Conceptually yes — find the direct MP3 URL from the episode page or RSS, paste. URL patterns differ slightly per host."},
            {"q": "Does Buzzsprout do its own transcription?", "a": "They partner with third parties for auto-transcripts (paid add-on). If you don't want to pay for that and you have a TranscriptX subscription, use us instead."},
            {"q": "Can I batch-transcribe a whole show's archive?", "a": "Yes, on our batch tier. Paste one MP3 URL per line from the RSS feed. Large archives take time but the process is automated."},
        ],
        "related_slugs": ["transcribe-mp3-from-url", "apple-podcasts", "transcribe-spotify-podcast"],
    },
    "jitsi-meet": {
        "slug": "jitsi-meet",
        "display": "Jitsi Meet",
        "title": "How to Transcribe a Jitsi Meet Recording",
        "h1": "How to Transcribe a Jitsi Meet Recording",
        "meta_title": "Transcribe Jitsi Meet Recording — Open-Source Meeting to Text | TranscriptX",
        "meta_description": "Jitsi Meet recordings save locally or to Dropbox/YouTube/etc. Wherever the recording lives, get a share URL and paste on TranscriptX.",
        "quick_answer": "Jitsi Meet doesn't host recordings itself — it writes to wherever you configured (Dropbox, YouTube Live, local file). Grab a share link from that destination and paste on TranscriptX.",
        "url_example": "https://www.dropbox.com/s/abc123/meeting-recording.mp4",
        "steps": [
            {"heading": "Locate where the recording was saved", "body": "Jitsi Meet asks the meeting organizer to pick a destination: Dropbox, YouTube Live stream, or local download. Check with the host.", "screenshot": None},
            {"heading": "Get a shareable URL from that destination", "body": "For Dropbox: Copy Link. For YouTube: use the Unlisted URL. For local files: upload to Drive/Dropbox first.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste the URL from wherever the recording lives.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Recording wasn't saved", "body": "Jitsi Meet doesn't auto-save anything. If nobody pressed Start Recording, or the destination wasn't configured, there's no file."},
            {"title": "Self-hosted Jibri (Jitsi Broadcasting Infrastructure) storage", "body": "Custom Jitsi deployments sometimes use self-hosted recording storage (Jibri + Nextcloud, etc.). If the link is internal-only, we can't reach it."},
            {"title": "YouTube Live stream recording in private mode", "body": "If the YouTube live-stream destination was set to Private, follow the <a href=\"/guides/transcribe-private-youtube-video\">private YouTube guide</a> — flip to Unlisted for the retry."},
            {"title": "meet.jit.si public server rate-limits", "body": "Doesn't affect transcription directly (we get the URL from the destination, not Jitsi itself)."},
        ],
        "faqs": [
            {"q": "Does Jitsi Meet have its own transcription feature?", "a": "Jitsi has a beta transcription plugin (Jigasi) for self-hosters, but it's not enabled on the public meet.jit.si by default. External transcription is the common path."},
            {"q": "What about 8x8 Jitsi (the commercial version)?", "a": "8x8's commercial Jitsi includes recording-to-their-cloud. Get a share link from the 8x8 dashboard and paste like any other cloud host."},
            {"q": "Is my Jitsi meeting really private if I transcribe it externally?", "a": "Depends on how the recording was shared. If you shared publicly, anyone can access. If you want maximum privacy, download locally, run transcription through a private service or self-hosted Whisper."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-google-drive-video", "google-meet"],
    },
    "whereby": {
        "slug": "whereby",
        "display": "Whereby",
        "title": "How to Transcribe a Whereby Meeting Recording",
        "h1": "How to Transcribe a Whereby Meeting Recording",
        "meta_title": "Transcribe Whereby Recording — Browser Meeting to Text | TranscriptX",
        "meta_description": "Whereby meeting recordings download as MP4s. Upload to Drive, share publicly, paste on TranscriptX for the transcript.",
        "quick_answer": "Whereby records locally to your computer when you click Record during a meeting. You get an MP4 file. Upload it to Google Drive with \"Anyone with the link\" access, paste the Drive URL on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Find the MP4 on your computer", "body": "Whereby saves recordings to your Downloads folder by default. Look for a .mp4 with the date + meeting name.", "screenshot": None},
            {"heading": "Upload to Google Drive (or Dropbox)", "body": "See <a href=\"/guides/transcribe-google-drive-video\">our Drive guide</a>. Upload the MP4, set sharing to <strong>Anyone with the link</strong>, copy.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Recording wasn't saved", "body": "Whereby only records when you click Record. If nobody did, there's no file."},
            {"title": "Multi-participant recording quirks", "body": "Whereby sometimes generates per-participant tracks instead of one merged video. If you have multiple MP4s, pick the one with the merged audio, or upload the one you want transcribed."},
            {"title": "Browser crash during record", "body": "If your browser crashed mid-meeting, the recording may be corrupted. Try the Whereby \"download crash recovery\" feature first."},
            {"title": "Whereby Embedded / custom deployments", "body": "Whereby Embedded (their SaaS for developers) can route recordings to cloud storage directly. Grab the URL from your own cloud destination."},
        ],
        "faqs": [
            {"q": "Does Whereby have built-in transcription?", "a": "Yes — they added a beta transcription feature. If it works for you, you don't need us. If you want cleaner text or SRT export, paste through TranscriptX."},
            {"q": "Is Whereby better for privacy than Zoom?", "a": "They're browser-based with some privacy advantages, but once you've saved a recording and uploaded it to Drive, the privacy story is the same as Zoom."},
            {"q": "What about very short Whereby meetings (under 5 minutes)?", "a": "Transcribes fine. Short files process quickly."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-google-drive-video", "google-meet"],
    },
    "riverside-fm": {
        "slug": "riverside-fm",
        "display": "Riverside.fm",
        "title": "How to Transcribe a Riverside.fm Recording",
        "h1": "How to Transcribe a Riverside.fm Recording",
        "meta_title": "Transcribe Riverside.fm Recording — Podcast / Interview | TranscriptX",
        "meta_description": "Riverside records locally per-participant and syncs up. Export the final audio, upload to Drive, paste on TranscriptX.",
        "quick_answer": "Riverside records each participant's audio on-device and uploads separately. After the session, export the merged audio (or the combined MP4), upload to Google Drive, share with Anyone-with-the-link, paste on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Wait for all local tracks to upload", "body": "Riverside finishes uploading per-participant tracks after the session. Don't export until the progress bar hits 100%.", "screenshot": None},
            {"heading": "Export the merged audio/video", "body": "In the Riverside dashboard → export → pick \"All tracks mixed\" for a single merged file.", "screenshot": None},
            {"heading": "Upload to Drive, paste the link", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste the Drive URL on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Tracks not fully uploaded", "body": "If a participant had a poor connection, their local track may not have uploaded. The merge will be missing their audio. Wait longer, or redo the interview."},
            {"title": "Riverside has its own transcription feature", "body": "Included on some plans. If it's good enough for your needs, you don't need us. If you want cleaner multi-format export, paste through TranscriptX."},
            {"title": "Multi-track export vs merged", "body": "For speaker labels, export multi-track, transcribe each separately, combine. See <a href=\"/guides/transcribe-multi-speaker-video\">our diarization guide</a>."},
        ],
        "faqs": [
            {"q": "Why is this better than just using Riverside's transcription?", "a": "Riverside's built-in transcript is convenient. We're useful if you need better accuracy on non-English audio, multi-format export, or if you're on a Riverside tier that doesn't include transcription."},
            {"q": "Does it work for Riverside video sessions (not just audio)?", "a": "Yes. Export the MP4 and the flow is identical."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-google-drive-video", "transcribe-multi-speaker-video"],
    },
    "squadcast": {
        "slug": "squadcast",
        "display": "SquadCast",
        "title": "How to Transcribe a SquadCast Recording",
        "h1": "How to Transcribe a SquadCast Recording",
        "meta_title": "Transcribe SquadCast Recording — Remote Podcast to Text | TranscriptX",
        "meta_description": "SquadCast stores each participant's audio separately. Export the merged file from your session dashboard, upload to Drive, paste on TranscriptX.",
        "quick_answer": "In your SquadCast session dashboard, download the combined MP3 or MP4 (not individual participant files, unless you want speaker-labeled transcription). Upload to Google Drive with Anyone-with-the-link, paste the Drive URL on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Open your SquadCast session dashboard", "body": "Sign in to SquadCast, find the session under Recordings.", "screenshot": None},
            {"heading": "Download the merged file", "body": "Choose \"Download mixed\" for a single file with all participants merged. Or \"Download tracks\" for per-speaker files.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Recording still processing", "body": "SquadCast takes a few minutes post-session to merge tracks. Don't download before it's ready."},
            {"title": "Descript integration changes things", "body": "SquadCast was acquired by Descript. Check your account — newer sessions may route through Descript's UI. Same underlying recording, slightly different export path."},
            {"title": "Multi-speaker diarization", "body": "For speaker labels, export per-track and transcribe each separately."},
        ],
        "faqs": [
            {"q": "Does SquadCast have its own transcription?", "a": "Yes on some plans, especially post-Descript-acquisition. If it works for you, use it. We're the alternative for better accuracy or multi-format export."},
            {"q": "What if one participant's audio is missing?", "a": "If their local track failed to upload, it's gone. SquadCast's local-first recording is more resilient than server-only, but not bulletproof."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "riverside-fm", "transcribe-multi-speaker-video"],
    },
    "podcastle": {
        "slug": "podcastle",
        "display": "Podcastle",
        "title": "How to Transcribe a Podcastle Recording",
        "h1": "How to Transcribe a Podcastle Recording",
        "meta_title": "Transcribe Podcastle Recording — Interview or Solo to Text | TranscriptX",
        "meta_description": "Podcastle stores sessions in the cloud. Export the merged MP3 or MP4, upload to Drive, paste on TranscriptX for the transcript.",
        "quick_answer": "After your Podcastle session, export the finished audio or video (Podcastle calls this \"Download\" from your project dashboard). Upload the file to Google Drive with Anyone-with-the-link, paste the Drive URL on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Open your Podcastle project", "body": "In the Podcastle web app, open the session project you want to transcribe.", "screenshot": None},
            {"heading": "Export / Download the final file", "body": "Click Export → pick MP3 (audio) or MP4 (video). Download to your computer.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Podcastle's AI tools are in the output", "body": "If you applied Magic Dust / AI audio cleanup, the transcription runs on the cleaned version — usually higher accuracy. Good."},
            {"title": "Free-tier export limits", "body": "Free Podcastle has export duration caps. If your session is longer than the cap, export trims it — transcribe only what you can export."},
            {"title": "Auto-generated transcript already included", "body": "Podcastle's own transcript is included on most paid plans. If it's good enough for your use, you don't need us. If you want cleaner output or SRT/VTT export, use TranscriptX."},
        ],
        "faqs": [
            {"q": "Why would I use TranscriptX when Podcastle has transcription?", "a": "Podcastle's is good but locked in their format. We output SRT/VTT/plain text with timestamps. Better if you need to drop captions into a video editor or a blog post."},
            {"q": "Does this work for video podcasts on Podcastle?", "a": "Yes. Export as MP4, upload, paste — same flow."},
        ],
        "related_slugs": ["riverside-fm", "squadcast", "transcribe-google-drive-video"],
    },
    "zencastr": {
        "slug": "zencastr",
        "display": "Zencastr",
        "title": "How to Transcribe a Zencastr Recording",
        "h1": "How to Transcribe a Zencastr Recording",
        "meta_title": "Transcribe Zencastr Recording — Podcast Session to Text | TranscriptX",
        "meta_description": "Zencastr records per-participant tracks in the cloud. Export the combined session audio, upload to Drive, paste on TranscriptX.",
        "quick_answer": "After a Zencastr session, wait for all tracks to finish uploading, then export either the combined audio or per-track files. Upload to Google Drive, paste the Drive URL on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Wait for tracks to upload", "body": "Zencastr's \"post-production upload\" for participants can take minutes to hours after the session. Export only when all tracks are fully uploaded.", "screenshot": None},
            {"heading": "Export combined or per-track audio", "body": "For single-transcript-all-speakers, export combined. For speaker-labeled output, export per-track (separate file per participant).", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Participant's track didn't upload", "body": "If someone closed their browser before post-upload finished, their track is lost. Zencastr does aggressive local recording as a backup, but not always."},
            {"title": "Free tier has limits on track count", "body": "Free Zencastr caps number of participants. If you hit that, tracks get merged before upload — harder to speaker-label later."},
            {"title": "Zencastr's own automated transcription", "body": "Paid Zencastr includes built-in transcription. Use it if it's enough. Use us for better multi-format export or to cross-check."},
        ],
        "faqs": [
            {"q": "Should I use combined or per-track export?", "a": "Combined is simpler — one file, one transcript. Per-track is better if you want labeled \"Speaker A: ... / Speaker B: ...\" output. See <a href=\"/guides/transcribe-multi-speaker-video\">our diarization guide</a>."},
            {"q": "What about Zencastr VideoChat sessions?", "a": "Same flow: export the combined video, upload to Drive, paste. Video processing takes proportionally longer."},
        ],
        "related_slugs": ["riverside-fm", "squadcast", "transcribe-multi-speaker-video"],
    },
    "descript": {
        "slug": "descript",
        "display": "Descript",
        "title": "How to Transcribe Descript Project Audio (Outside Descript)",
        "h1": "How to Transcribe Descript Project Audio",
        "meta_title": "Transcribe Descript Project — Bypass Descript's Transcript | TranscriptX",
        "meta_description": "Descript transcribes everything inside the app already. Use TranscriptX if you need to transcribe the source audio in a cleaner pipeline or export to SRT/VTT that matches another tool.",
        "quick_answer": "Descript projects have built-in transcripts — that's the whole product. The main reasons to run transcription elsewhere: you want SRT/VTT that matches a different timestamp system, you want to compare accuracy, or the project is exported as audio and you want a clean transcript in another format. Export the composition audio, upload to Drive, paste on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Export your Descript composition's audio", "body": "In Descript, Publish → Export → Audio → WAV or MP3.", "screenshot": None},
            {"heading": "Upload to Drive, share", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a>.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste the Drive URL.", "screenshot": None},
        ],
        "breaks": [
            {"title": "You probably don't need this", "body": "Descript's native transcription is the product. If it works for your use case, skip external transcription. We're useful for edge cases or comparison only."},
            {"title": "Edited timeline vs original audio", "body": "Descript's transcript matches the edited timeline. If you transcribe the exported audio externally, timestamps will match the export — not the original recording."},
            {"title": "SquadCast now runs on Descript", "body": "SquadCast was acquired by Descript. If your session is a post-acquisition SquadCast export, it's effectively Descript."},
        ],
        "faqs": [
            {"q": "Why would I use TranscriptX when Descript already transcribes?", "a": "Mostly for format flexibility (SRT/VTT in the format another tool expects) or if you want to double-check accuracy. Most Descript users should just use Descript's built-in transcript."},
            {"q": "Does this handle the Descript Studio Sound clean-up?", "a": "Yes — transcription runs on whatever audio you export. Studio Sound-processed audio usually transcribes more cleanly."},
        ],
        "related_slugs": ["riverside-fm", "squadcast", "podcastle"],
    },
    "udemy": {
        "slug": "udemy",
        "display": "Udemy",
        "title": "How to Transcribe a Udemy Course Video (What Actually Works)",
        "h1": "How to Transcribe a Udemy Course Video",
        "meta_title": "Transcribe Udemy Course Video — Subtitles or Download | TranscriptX",
        "meta_description": "Udemy videos are behind a paid enrollment wall. External tools can't fetch them directly. Here's the honest version of what works.",
        "quick_answer": "Udemy course videos require enrollment to access. External tools can't authenticate. If you're enrolled, download the video via Udemy's mobile app (which allows offline viewing), then transfer the file, upload to Drive, paste on TranscriptX. Free courses follow the same rule — paid or free, they're still auth-gated.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Install the Udemy mobile app and download the lecture", "body": "Offline downloads are a student-only feature. Each lecture downloads as a video file locally.", "screenshot": None},
            {"heading": "Transfer the file to your computer", "body": "Airdrop, USB, or cloud sync the video off your phone.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Udemy has its own captions already", "body": "Most Udemy courses include captions the instructor uploaded or Udemy auto-generated. Those might be enough — check first."},
            {"title": "Downloads disabled by instructor", "body": "Some instructors turn off offline downloads. If disabled, no honest path exists."},
            {"title": "Copyright and course usage terms", "body": "Udemy's terms limit what you can do with course content. Personal-use transcripts are typically fine; publishing them publicly isn't."},
        ],
        "faqs": [
            {"q": "Isn't Udemy's own transcript enough?", "a": "Usually yes — Udemy's captions are included on most courses. The only reason to run external transcription is if you want a different format or need transcripts for courses without captions."},
            {"q": "What about Udemy Business for my company?", "a": "Same rule. Corporate enrollment still requires auth. Download via the mobile app if allowed by your org."},
        ],
        "related_slugs": ["coursera", "transcribe-lecture-for-study-notes", "transcribe-google-drive-video"],
    },
    "coursera": {
        "slug": "coursera",
        "display": "Coursera",
        "title": "How to Transcribe a Coursera Lecture Video",
        "h1": "How to Transcribe a Coursera Lecture Video",
        "meta_title": "Transcribe Coursera Lecture — Auditor or Paid Access | TranscriptX",
        "meta_description": "Coursera's lectures include transcripts for enrolled students already. For external use or different formats, download the video and re-transcribe.",
        "quick_answer": "Coursera includes transcripts on most lectures — check the Transcript tab first. If you need a different format, download the lecture (available for enrolled / audited / paid students), upload to Drive, paste on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Check Coursera's built-in transcript tab first", "body": "Most Coursera lectures have a Transcript tab under the video. Download option is usually available for enrolled students.", "screenshot": None},
            {"heading": "If you need different format, download the video", "body": "Below the video → download → pick a resolution. You'll get an MP4.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Paid-only specializations", "body": "Specializations and Coursera Plus content require a subscription. Same rule — you must be enrolled to download."},
            {"title": "Download disabled by instructor", "body": "Partners can disable student downloads. Not common, but it happens. Auditor flow still lets you stream in the browser."},
            {"title": "Coursera's transcript is usually already good", "body": "Most users don't need external transcription of Coursera lectures. Check the Transcript tab first before downloading."},
        ],
        "faqs": [
            {"q": "Can I use the existing Coursera transcript?", "a": "Yes. The Transcript tab usually has a Download button. That's probably what you want — faster than re-transcribing."},
            {"q": "What about Coursera for Business / Coursera Plus?", "a": "Same flow. Enrollment gives you downloads; the rest is identical."},
        ],
        "related_slugs": ["udemy", "transcribe-lecture-for-study-notes", "transcribe-google-drive-video"],
    },
    "kajabi": {
        "slug": "kajabi",
        "display": "Kajabi",
        "title": "How to Transcribe a Kajabi Course Video",
        "h1": "How to Transcribe a Kajabi Course Video",
        "meta_title": "Transcribe Kajabi Course — Creator or Student Access | TranscriptX",
        "meta_description": "Kajabi hosts creators' course videos behind enrollment walls. If you own the course, export the video directly. Students need to work from their enrolled session.",
        "quick_answer": "If you own the Kajabi course: export the video from your Kajabi admin. If you're a student: download the lecture (if the creator enabled it), upload to Drive, paste on TranscriptX. Kajabi doesn't have built-in transcription — you'll need external tools like us.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Creator: export from your admin", "body": "In your Kajabi admin, open the course → lesson → download the original video file.", "screenshot": None},
            {"heading": "Student: download via enrolled session", "body": "If the creator enabled downloads on the lesson, right-click the video player → Save video. Otherwise, request the file from the creator.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Kajabi doesn't include transcription", "body": "Unlike Coursera/Udemy, Kajabi has no built-in transcripts. External transcription (us, or another service) is required."},
            {"title": "Downloads disabled on the course", "body": "Creators can disable student downloads. Students have to ask the creator for the file, or settle for no transcript."},
            {"title": "Video hosted on Wistia under Kajabi", "body": "Kajabi uses Wistia under the hood for video hosting. Some flows work better by going through Wistia directly — see <a href=\"/how-to-transcribe/wistia\">our Wistia guide</a>."},
        ],
        "faqs": [
            {"q": "Why does Kajabi need external transcription?", "a": "Kajabi focuses on course delivery + payments, not transcription. Most creators add transcripts manually or use a service like us."},
            {"q": "What about Kajabi communities / coaching videos?", "a": "Same flow — all video on Kajabi is hostable on Wistia. Get the file or share URL, paste."},
        ],
        "related_slugs": ["wistia", "udemy", "transcribe-google-drive-video"],
    },
    "teachable": {
        "slug": "teachable",
        "display": "Teachable",
        "title": "How to Transcribe a Teachable Course Video",
        "h1": "How to Transcribe a Teachable Course Video",
        "meta_title": "Transcribe Teachable Course — Creator or Student Workflow | TranscriptX",
        "meta_description": "Teachable hosts course videos on Wistia or Vimeo under the hood. Get the source file, upload to Drive, paste on TranscriptX.",
        "quick_answer": "Creators: export the video from your Teachable admin (or re-upload your original source file). Students: if downloads are enabled, grab the file; otherwise ask the creator. Upload to Drive, paste on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Creator: export from Teachable admin", "body": "Admin → School → Curriculum → the lecture. Download the source video.", "screenshot": None},
            {"heading": "Student: student downloads if enabled", "body": "Below the video, if the creator enabled downloads, right-click Save.", "screenshot": None},
            {"heading": "Upload to Drive, paste", "body": "<a href=\"/guides/transcribe-google-drive-video\">Drive flow</a> → paste on <a href=\"/\">TranscriptX</a>.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Teachable doesn't transcribe natively", "body": "Like Kajabi, Teachable is course-delivery focused. External transcription is the standard path."},
            {"title": "Student downloads disabled", "body": "If the creator blocks downloads, students can't grab the file. Ask the creator."},
            {"title": "Hosted on Wistia / Vimeo underneath", "body": "Depending on the Teachable plan, videos may be hosted on Wistia or Vimeo. Sometimes going through those platforms directly is easier — see our <a href=\"/how-to-transcribe/wistia\">Wistia</a> and <a href=\"/guides/transcribe-vimeo-video\">Vimeo</a> guides."},
        ],
        "faqs": [
            {"q": "Is this different from Kajabi?", "a": "Same conceptual flow. URL patterns and admin UI differ. Kajabi leans Wistia; Teachable uses Wistia or Vimeo. Grab the source file either way."},
            {"q": "What about Teachable:u (the student app)?", "a": "Same rule — authentication required, creator-enabled downloads only."},
        ],
        "related_slugs": ["kajabi", "wistia", "transcribe-vimeo-video"],
    },
    "ringcentral-video": {
        "slug": "ringcentral-video",
        "display": "RingCentral Video (formerly Glip)",
        "title": "How to Transcribe a RingCentral Video Meeting Recording",
        "h1": "How to Transcribe a RingCentral Video Meeting Recording",
        "meta_title": "Transcribe RingCentral Video Meeting — Enterprise Recording | TranscriptX",
        "meta_description": "RingCentral Video (formerly Glip) saves meeting recordings to the cloud. Share externally or download, upload to Drive, paste on TranscriptX.",
        "quick_answer": "RingCentral Video meeting recordings save to the organizer's RingCentral cloud. Share externally (if your admin allows), or download the MP4 and upload to Google Drive. Paste the resulting URL on TranscriptX.",
        "url_example": "https://drive.google.com/file/d/FILEID/view",
        "steps": [
            {"heading": "Open the recording in RingCentral", "body": "Sign in to RingCentral app or web → Recordings.", "screenshot": None},
            {"heading": "Share or download", "body": "If your admin allows external sharing, copy the public link. Otherwise download the MP4 and upload to Drive.", "screenshot": None},
            {"heading": "Paste on TranscriptX", "body": "<a href=\"/\">transcriptx.xyz</a> → paste.", "screenshot": None},
        ],
        "breaks": [
            {"title": "Admin-restricted external sharing", "body": "Enterprise RingCentral often locks external sharing. Download + Drive fallback is the workaround."},
            {"title": "Recording expired", "body": "RingCentral has retention limits per plan. Past the window, the file is gone."},
            {"title": "Password-protected recording", "body": "Can't type passwords. Remove password or use the Drive fallback."},
        ],
        "faqs": [
            {"q": "Is this the same as Glip?", "a": "Yes. Glip was RingCentral's earlier name for this product. The recording storage and share flow is the same."},
            {"q": "Does RingCentral have its own transcription?", "a": "Yes on some tiers. If included and good enough, use it. We're the alternative for multi-format export or cross-checking."},
        ],
        "related_slugs": ["transcribe-zoom-recording", "transcribe-microsoft-teams-recording", "google-meet"],
    },
}


def current_lastmod():
    return datetime.now(timezone.utc).date().isoformat()


def get_static_seo_paths():
    paths = [page["path"] for page in HEAD_TERM_PAGES.values()]
    paths.extend([f"/compare/{slug}" for slug in COMPARISON_PAGES])
    paths.extend([f"/research/{slug}" for slug in RESEARCH_PAGES])
    paths.extend([f"/help/{slug}" for slug in HELP_PAGES])
    paths.extend([f"/for/{slug}" for slug in PERSONA_PAGES])
    paths.extend([f"/category/{slug}" for slug in PLATFORM_CATEGORIES])
    paths.extend([f"/how-to-transcribe/{slug}" for slug in PLATFORM_GUIDES])
    paths.append("/help")
    paths.append("/categories")
    paths.append("/press-kit")
    return paths
