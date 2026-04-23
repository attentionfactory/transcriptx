"""
error_classifier.py — Unified error classification for user-facing messages
============================================================================
Maps raw exceptions and error strings to structured, actionable error responses.
"""

import re


def classify_user_error(error_message, context="transcription"):
    """
    Classify an error into a user-friendly structured response.

    Args:
        error_message (str): Raw error string from exception or subprocess
        context (str): What operation failed ("transcription", "download", "metadata")

    Returns:
        dict: {
            "message": str,        # User-readable error message
            "action": str,         # What the user should do next
            "help_url": str,       # Link to help page
            "severity": str,       # "user_error", "rate_limit", "service_error", "unknown"
            "retry_after": int,    # Seconds to wait before retry (if applicable)
        }
    """
    if not error_message:
        return _unknown_error(context)

    msg = str(error_message).lower()

    # ============================================================
    # PRIVATE / RESTRICTED VIDEO
    # ============================================================
    if any(x in msg for x in ["private video", "is private", "members-only", "sign in to confirm"]):
        return {
            "message": "This video is private or restricted",
            "action": "Change it to Public or Unlisted, or make sure you're using the correct share link",
            "help_url": "/help/private-video-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # VIDEO UNAVAILABLE / REMOVED
    # ============================================================
    if any(x in msg for x in ["video unavailable", "video is unavailable", "no longer available", "removed by the uploader", "has been removed"]):
        return {
            "message": "This video is no longer available",
            "action": "The video may have been deleted or made private by the uploader",
            "help_url": "/help",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # AGE-RESTRICTED
    # ============================================================
    if any(x in msg for x in ["age-restricted", "age restricted", "sign in to confirm your age"]):
        return {
            "message": "This video is age-restricted",
            "action": "Age-restricted videos can't be transcribed automatically. Try downloading it first, then upload the file.",
            "help_url": "/help",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # REGION-LOCKED / GEO-BLOCKED
    # ============================================================
    if any(x in msg for x in ["geo", "region", "not available in your country", "blocked in your country"]):
        return {
            "message": "This video is region-locked",
            "action": "The video is blocked in our servers' location (US). Try the original platform or find a mirror.",
            "help_url": "/help/region-locked-video-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # UNSUPPORTED URL / NO VIDEO FOUND
    # ============================================================
    if any(x in msg for x in ["unsupported url", "no video found", "no video formats found", "no video at this url"]):
        return {
            "message": "We couldn't find a video at this URL",
            "action": "Make sure you're using the video page URL (not a share link or embed). Some sites require direct file upload instead.",
            "help_url": "/help/upload-audio-file-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # RATE LIMIT / TOO MANY REQUESTS
    # ============================================================
    if any(x in msg for x in ["429", "too many requests", "rate limit", "http error 429"]):
        # Try to extract retry-after if present
        retry_match = re.search(r"retry[- ]after[:\s]+(\d+)", msg)
        retry_seconds = int(retry_match.group(1)) if retry_match else 60

        return {
            "message": "Rate limit reached",
            "action": f"Wait {retry_seconds} seconds and try again. If this keeps happening, contact support.",
            "help_url": "/help",
            "severity": "rate_limit",
            "retry_after": retry_seconds,
        }

    # ============================================================
    # TIMEOUT
    # ============================================================
    if any(x in msg for x in ["timed out", "timeout", "time out"]):
        return {
            "message": "Request timed out",
            "action": "This video took too long to process. Try again with a shorter video, or contact support if it keeps failing.",
            "help_url": "/help",
            "severity": "service_error",
            "retry_after": 0,
        }

    # ============================================================
    # FILE TOO LARGE
    # ============================================================
    if any(x in msg for x in ["too large", "file size exceeds", "audio too large"]):
        size_match = re.search(r"(\d+(?:\.\d+)?)\s*mb", msg)
        size_str = size_match.group(1) + "MB" if size_match else "file"

        return {
            "message": f"File too large ({size_str})",
            "action": "Maximum file size is 25MB. Try a shorter video or upgrade your plan for larger files.",
            "help_url": "/help",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # FORBIDDEN / 403
    # ============================================================
    if any(x in msg for x in ["403", "forbidden", "access denied"]):
        return {
            "message": "Access forbidden",
            "action": "This content may be login-protected or blocked. Make sure the video is publicly accessible.",
            "help_url": "/help/private-video-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # YOUTUBE ANTI-BOT
    # ============================================================
    if any(x in msg for x in ["anti-bot", "login_required", "sign in to confirm you"]):
        return {
            "message": "YouTube temporarily blocked our request",
            "action": "Try again in a few minutes. YouTube sometimes requires additional verification.",
            "help_url": "/help",
            "severity": "service_error",
            "retry_after": 120,
        }

    # ============================================================
    # INSTAGRAM STORIES
    # ============================================================
    if "instagram" in msg and ("story" in msg or "stories" in msg):
        return {
            "message": "Instagram Stories are unreliable to transcribe",
            "action": "Instagram blocks most automated Story downloads. Screen-record to your camera roll, then upload the file.",
            "help_url": "/help/instagram-story-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # GOOGLE DRIVE FOLDER URL
    # ============================================================
    if "drive.google.com" in msg and ("folder" in msg or "folders" in msg):
        return {
            "message": "This looks like a Google Drive folder URL",
            "action": "Open the specific file in Google Drive and copy that URL instead of the folder URL.",
            "help_url": "/help/google-drive-transcript-link",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # NO AUDIO FILE FOUND
    # ============================================================
    if any(x in msg for x in ["no audio file found", "no mp4 file produced"]):
        return {
            "message": "Couldn't extract audio from this video",
            "action": "The video may use an unsupported format. Try uploading the file directly instead of a URL.",
            "help_url": "/help/upload-audio-file-transcript",
            "severity": "user_error",
            "retry_after": 0,
        }

    # ============================================================
    # GROQ API ERRORS
    # ============================================================
    if any(x in msg for x in ["groq", "api error", "model not found"]):
        return {
            "message": "Transcription service error",
            "action": "Our transcription service is temporarily unavailable. Try again in a few minutes.",
            "help_url": "/help",
            "severity": "service_error",
            "retry_after": 60,
        }

    # ============================================================
    # NETWORK / CONNECTION ERRORS
    # ============================================================
    if any(x in msg for x in ["connection", "network", "unable to download", "failed to connect"]):
        return {
            "message": "Network connection error",
            "action": "We couldn't reach the video source. Check that the URL is valid and try again.",
            "help_url": "/help",
            "severity": "service_error",
            "retry_after": 30,
        }

    # ============================================================
    # FALLBACK: UNKNOWN ERROR
    # ============================================================
    return _unknown_error(context, error_message)


def _unknown_error(context="operation", raw_error=None):
    """Fallback for errors we can't classify."""
    # Truncate raw error to avoid leaking sensitive internals
    safe_error = str(raw_error)[:100] if raw_error else ""

    return {
        "message": f"Something went wrong with {context}",
        "action": "Try again or contact support if this keeps happening",
        "help_url": "/help",
        "severity": "unknown",
        "retry_after": 0,
        "debug": safe_error,  # Only for support/debugging
    }


def format_error_response(error_message, context="transcription"):
    """
    Convenience wrapper that returns a JSON-ready error response.

    Usage in Flask:
        result = format_error_response(str(e), "video download")
        return jsonify(result), 400
    """
    classified = classify_user_error(error_message, context)

    response = {
        "status": "error",
        "error": classified["message"],
        "action": classified["action"],
        "help_url": classified["help_url"],
    }

    if classified.get("retry_after", 0) > 0:
        response["retry_after"] = classified["retry_after"]

    # Include debug info only in non-user_error cases
    if classified["severity"] != "user_error" and "debug" in classified:
        response["debug"] = classified["debug"]

    return response
