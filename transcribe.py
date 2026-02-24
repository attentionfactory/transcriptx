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
from groq import Groq

log = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not set")
        _client = Groq(api_key=key)
    return _client


def get_metadata(url):
    """Pull video metadata via yt-dlp (no download)."""
    try:
        r = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", "--no-playlist", url],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            return {"error": f"Could not fetch video: {r.stderr.strip()[:200]}"}

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
        r = subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "-f", "bestaudio/best",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "9",
                "-o", out,
                url
            ],
            capture_output=True, text=True, timeout=120
        )

        dl_time = time.time() - t0
        log.info("[download] yt-dlp finished in %.1fs, exit=%d", dl_time, r.returncode)

        if r.returncode != 0:
            log.error("[download] yt-dlp failed: %s", r.stderr.strip()[:200])
            return None, f"Download failed: {r.stderr.strip()[:200]}"

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
            )
        elapsed = time.time() - t0
        lang = getattr(result, "language", "unknown")
        log.info("[transcribe] done in %.1fs lang=%s chars=%d", elapsed, lang, len(result.text))
        return {
            "transcript": result.text.strip(),
            "language": lang,
        }
    except Exception as e:
        log.exception("[transcribe] failed after %.1fs", time.time() - t0)
        return {"transcript": "", "error": str(e)}


def process_url(url, model="whisper-large-v3-turbo"):
    """Full pipeline: URL → metadata + transcript."""
    log.info("[pipeline] start url=%s model=%s", url, model)
    t_total = time.time()

    meta = get_metadata(url)
    if "error" in meta:
        log.warning("[pipeline] metadata error: %s", meta["error"])
        return {"url": url, "status": "error", "error": meta["error"]}

    # Download
    filepath, err = download_audio(url)
    if err:
        return {
            "url": url,
            "status": "error",
            "error": err,
            **{k: meta.get(k, 0) for k in ["views", "likes", "comments", "duration"]},
        }

    # Transcribe
    result = transcribe(filepath, model)

    # Cleanup
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

    return {
        "url": url,
        "status": status,
        "transcript": result.get("transcript", ""),
        "language": result.get("language", "unknown"),
        "views": meta.get("views", 0),
        "likes": meta.get("likes", 0),
        "comments": meta.get("comments", 0),
        "duration": dur,
        "duration_formatted": dur_fmt,
        "uploader": meta.get("uploader", ""),
        "error": result.get("error"),
    }