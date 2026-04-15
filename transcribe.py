"""
transcribe.py — Groq Whisper + yt-dlp
=======================================
Download audio from URL, transcribe with Groq, return result.
"""

import os
import json
import logging
import subprocess
import tempfile
import time
import re
from groq import Groq

log = logging.getLogger(__name__)

_client = None
_YTDLP_RETRY_ARGS = [
    "--extractor-retries", "3",
    "--retries", "5",
    "--fragment-retries", "5",
    "--sleep-requests", "1",
    "--socket-timeout", "30",
]
_YT_ANTIBOT_MARKERS = (
    "http error 429",
    "login_required",
    "sign in to confirm you",
    "unable to download webpage",
)

# Substrings (case-insensitive) that indicate the user's input is the problem
# (private/unsupported/missing video) rather than a transient upstream issue.
# We still did real work on these, so we don't refund the credit.
_USER_INPUT_ERROR_MARKERS = (
    "no video found",
    "private video",
    "is private",
    "video unavailable",
    "video is unavailable",
    "this video is no longer available",
    "removed by the uploader",
    "members-only",
    "unsupported url",
    "audio too large",
    "no audio file found",
    "no mp4 file produced",
)


def classify_error(error_message):
    """Classify a process_url error string into 'user_input' or 'upstream'.

    user_input  → user supplied a bad URL / unsupported video; do NOT refund.
    upstream    → our problem (network, Groq, anti-bot block, timeout); DO refund.

    The default is 'upstream' so we err on the side of refunding when unsure.
    """
    msg = (error_message or "").lower()
    if not msg:
        return "upstream"
    for marker in _USER_INPUT_ERROR_MARKERS:
        if marker in msg:
            return "user_input"
    return "upstream"


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not set")
        _client = Groq(api_key=key)
    return _client


def _is_youtube_url(url):
    u = url.lower()
    return "youtube.com" in u or "youtu.be" in u


def _is_youtube_antibot(stderr):
    e = (stderr or "").lower()
    return any(marker in e for marker in _YT_ANTIBOT_MARKERS)


def _proxy_candidates():
    raw = os.environ.get("YTDLP_PROXY_URL", "").strip()
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def _format_yt_dlp_error(stderr, context, used_proxy=False):
    msg = (stderr or "").strip()
    if _is_youtube_antibot(msg):
        if used_proxy:
            return (
                f"{context} failed: YouTube anti-bot check blocked this request after proxy retry. "
                "Try again in a few minutes or use a different rotating proxy endpoint."
            )
        return (
            f"{context} failed: YouTube anti-bot check blocked this request "
            "(HTTP 429 / LOGIN_REQUIRED)."
        )

    if "timed out" in msg.lower():
        return f"{context} timed out while contacting the video source."

    short = msg[:220] if msg else "Unknown yt-dlp error"
    return f"{context} failed: {short}"


def _run_ytdlp_with_fallback(cmd, timeout, url):
    """Run yt-dlp directly; for YouTube anti-bot errors retry via proxy."""
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode == 0:
        return r, False

    if not _is_youtube_url(url) or not _is_youtube_antibot(r.stderr):
        return r, False

    proxies = _proxy_candidates()
    if not proxies:
        return r, False

    log.warning("[yt-dlp] YouTube anti-bot detected. Retrying with proxy pool (%d)", len(proxies))

    last = r
    for proxy in proxies:
        proxy_cmd = ["yt-dlp", "--proxy", proxy, *cmd[1:]]
        log.info("[yt-dlp] proxy retry using endpoint=%s", proxy.split("@")[-1])
        pr = subprocess.run(proxy_cmd, capture_output=True, text=True, timeout=timeout)
        last = pr
        if pr.returncode == 0:
            return pr, True

    return last, True


def get_metadata(url):
    """Pull video metadata via yt-dlp (no download)."""
    try:
        r, used_proxy = _run_ytdlp_with_fallback(
            ["yt-dlp", *_YTDLP_RETRY_ARGS, "--dump-json", "--no-download", "--no-playlist", url],
            timeout=60,
            url=url,
        )
        if r.returncode != 0:
            return {"error": _format_yt_dlp_error(r.stderr, "Could not fetch video metadata", used_proxy)}

        info = json.loads(r.stdout)
        return {
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "duration": info.get("duration", 0),
            "views": info.get("view_count", 0),
            "likes": info.get("like_count", 0),
            "comments": info.get("comment_count", 0),
            "upload_date": info.get("upload_date", ""),
            "uploader": info.get("uploader", ""),
            "thumbnail": info.get("thumbnail", ""),
            "id": info.get("id", ""),
        }
    except json.JSONDecodeError:
        return {"error": "No video found at this URL. Make sure it's a video, not an image or carousel."}
    except subprocess.TimeoutExpired:
        return {"error": "Timed out fetching video info"}
    except Exception as e:
        return {"error": str(e)}


def download_audio(url):
    """Download audio as mp3 via yt-dlp. Returns (filepath, error)."""
    tmpdir = tempfile.mkdtemp()
    out = os.path.join(tmpdir, "%(id)s.%(ext)s")

    log.info("[download] start url=%s", url)
    t0 = time.time()

    try:
        r, used_proxy = _run_ytdlp_with_fallback(
            [
                "yt-dlp",
                *_YTDLP_RETRY_ARGS,
                "--no-playlist",
                "-f", "bestaudio/best",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "9",
                "-o", out,
                url,
            ],
            timeout=120,
            url=url,
        )

        dl_time = time.time() - t0
        log.info("[download] yt-dlp finished in %.1fs, exit=%d", dl_time, r.returncode)

        if r.returncode != 0:
            log.error("[download] yt-dlp failed: %s", r.stderr.strip()[:200])
            return None, _format_yt_dlp_error(r.stderr, "Audio download", used_proxy)

        for f in os.listdir(tmpdir):
            if f.endswith((".mp3", ".wav", ".m4a", ".ogg", ".webm")):
                fp = os.path.join(tmpdir, f)
                size_mb = os.path.getsize(fp) / (1024 * 1024)
                log.info("[download] audio file=%s size=%.1fMB", f, size_mb)
                if size_mb > 25:
                    return None, f"Audio too large ({size_mb:.1f}MB, max 25MB)"
                return fp, None

        log.warning("[download] no audio file found in %s", tmpdir)
        return None, "No audio file found after download"
    except subprocess.TimeoutExpired:
        log.error("[download] timed out after 120s")
        return None, "Download timed out"
    except Exception as e:
        log.exception("[download] unexpected error")
        return None, str(e)


def transcribe(filepath, model="whisper-large-v3-turbo"):
    """Transcribe audio file with Groq Whisper."""
    client = _get_client()
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    log.info("[transcribe] start file=%s size=%.1fMB model=%s", os.path.basename(filepath), size_mb, model)
    t0 = time.time()
    try:
        with open(filepath, "rb") as f:
            result = client.audio.transcriptions.create(
                file=f,
                model=model,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
            )
        elapsed = time.time() - t0
        lang = getattr(result, "language", "unknown")
        log.info("[transcribe] done in %.1fs lang=%s chars=%d", elapsed, lang, len(result.text))

        # Groq SDK object can be pydantic-like; normalize for safe access.
        result_data = result.model_dump() if hasattr(result, "model_dump") else result
        segments = []
        words = []
        if isinstance(result_data, dict):
            segments = result_data.get("segments") or []
            words = result_data.get("words") or []
        else:
            # Groq SDK may return object-like responses with attrs.
            segments = getattr(result, "segments", None) or []
            words = getattr(result, "words", None) or []

        return {
            "transcript": result.text.strip(),
            "language": lang,
            "segments": segments,
            "words": words,
        }
    except Exception as e:
        log.exception("[transcribe] failed after %.1fs", time.time() - t0)
        return {"transcript": "", "error": str(e)}


def process_url(url, model="whisper-large-v3-turbo"):
    """Full pipeline: URL → metadata + transcript."""
    log.info("[pipeline] start url=%s model=%s", url, model)
    t_total = time.time()

    metadata_error = None
    meta = get_metadata(url)
    if "error" in meta:
        metadata_error = meta["error"]
        if _is_youtube_url(url):
            log.warning("[pipeline] metadata error (continuing for YouTube): %s", metadata_error)
            meta = {}
        else:
            log.warning("[pipeline] metadata error: %s", metadata_error)
            return {
                "url": url,
                "status": "error",
                "error": metadata_error,
                "error_kind": classify_error(metadata_error),
            }

    # Download
    filepath, err = download_audio(url)
    if err:
        return {
            "url": url,
            "status": "error",
            "error": err,
            "error_kind": classify_error(err),
            "metadata_error": metadata_error,
            **{k: meta.get(k, 0) for k in ["views", "likes", "comments", "duration"]},
        }

    try:
        result = transcribe(filepath, model)
    finally:
        try:
            os.remove(filepath)
            os.rmdir(os.path.dirname(filepath))
        except Exception:
            pass

    # Format duration
    dur = meta.get("duration", 0)
    dur_fmt = f"{int(dur)//60}m {int(dur)%60}s" if dur else "N/A"

    status = "error" if "error" in result else "success"
    log.info("[pipeline] done url=%s status=%s total=%.1fs", url, status, time.time() - t_total)

    payload = {
        "url": url,
        "status": status,
        "title": meta.get("title", ""),
        "thumbnail": meta.get("thumbnail", ""),
        "transcript": result.get("transcript", ""),
        "language": result.get("language", "unknown"),
        "segments": result.get("segments", []),
        "words": result.get("words", []),
        "views": meta.get("views", 0),
        "likes": meta.get("likes", 0),
        "comments": meta.get("comments", 0),
        "duration": dur,
        "duration_formatted": dur_fmt,
        "uploader": meta.get("uploader", ""),
        "metadata_error": metadata_error,
        "error": result.get("error"),
    }
    if status == "error":
        # Transcription stage errors (Groq) are upstream by default — operator
        # problem, not the user's. classify_error handles this conservatively.
        payload["error_kind"] = classify_error(result.get("error"))
    return payload


def _sanitize_filename(value, fallback="video"):
    raw = (value or "").strip()
    if not raw:
        raw = fallback
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", raw)[:120] or fallback


def download_video_mp4(url, output_dir):
    """Download best MP4 video+audio into output_dir. Returns (filepath, error)."""
    out = os.path.join(output_dir, "%(id)s.%(ext)s")
    try:
        r, used_proxy = _run_ytdlp_with_fallback(
            [
                "yt-dlp",
                *_YTDLP_RETRY_ARGS,
                "--no-playlist",
                "-f", "bv*+ba/b[ext=mp4]/b",
                "--merge-output-format", "mp4",
                "-o", out,
                url,
            ],
            timeout=240,
            url=url,
        )
        if r.returncode != 0:
            return None, _format_yt_dlp_error(r.stderr, "Video download", used_proxy)

        candidates = []
        for name in os.listdir(output_dir):
            p = os.path.join(output_dir, name)
            if os.path.isfile(p) and name.lower().endswith(".mp4"):
                candidates.append(p)
        if not candidates:
            return None, "No mp4 file produced by yt-dlp"
        candidates.sort(key=lambda p: os.path.getsize(p), reverse=True)
        return candidates[0], None
    except subprocess.TimeoutExpired:
        return None, "Video download timed out"
    except Exception as e:
        return None, str(e)


def clip_video_segment(input_file, output_file, start_seconds, end_seconds):
    """Clip a segment from input_file into output_file. Returns error or None."""
    try:
        # Fast path: stream copy (can fail if no keyframe near cut points).
        cmd_copy = [
            "ffmpeg",
            "-y",
            "-ss", str(start_seconds),
            "-to", str(end_seconds),
            "-i", input_file,
            "-c", "copy",
            output_file,
        ]
        r = subprocess.run(cmd_copy, capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return None

        # Fallback: re-encode for robust cuts.
        cmd_encode = [
            "ffmpeg",
            "-y",
            "-ss", str(start_seconds),
            "-to", str(end_seconds),
            "-i", input_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "+faststart",
            output_file,
        ]
        r2 = subprocess.run(cmd_encode, capture_output=True, text=True, timeout=240)
        if r2.returncode != 0 or not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            msg = (r2.stderr or r.stderr or "").strip()[:220]
            return f"ffmpeg clip failed: {msg or 'unknown error'}"
        return None
    except subprocess.TimeoutExpired:
        return "ffmpeg clip timed out"
    except Exception as e:
        return str(e)
