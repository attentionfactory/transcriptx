"""
spotify_resolver.py — turn a Spotify episode URL into a public podcast feed URL.

Spotify blocks scrapers, so yt-dlp cannot download Spotify episode audio. But
the same episode is almost always available via the show's public RSS feed.
This module does the lookup so the rest of the transcription pipeline can
treat Spotify URLs as if they were regular podcast URLs.

Flow:
  1. Spotify episode URL → public OG metadata (title + show name)
  2. Show name → iTunes Search API → RSS feed URL
  3. RSS feed → match episode by normalized title → MP3 enclosure URL

No API keys, no auth, no partnership. Verified working end-to-end. Returns
``None`` if any step fails so the caller can surface a clear error.
"""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urlparse

import requests

log = logging.getLogger(__name__)

_SPOTIFY_EPISODE_RE = re.compile(
    r"^https?://(?:open\.)?spotify\.com/(?:[a-z-]+/)?episode/[A-Za-z0-9]+",
    re.IGNORECASE,
)
_OG_TITLE_RE = re.compile(r'property="og:title"\s+content="([^"]+)"')
_OG_DESC_RE = re.compile(r'property="og:description"\s+content="([^"]+)"')

# Spotify serves a stripped HTML to "browser" User-Agents and the full
# OG-tagged page to link-unfurler bots. Identifying as facebookexternalhit
# is honest (we ARE here for the OG metadata, not to render the page) and
# returns ~30KB instead of ~74KB.
_OG_USER_AGENT = "facebookexternalhit/1.1"
# Generic UA for the iTunes API and RSS feeds (which don't care).
_DEFAULT_USER_AGENT = "TranscriptX/1.0 (+https://transcriptx.xyz)"
_HTTP_TIMEOUT = 10


def is_spotify_episode_url(url: str) -> bool:
    """True if `url` looks like a Spotify episode link we should try to resolve."""
    if not url:
        return False
    return bool(_SPOTIFY_EPISODE_RE.match(url.strip()))


def _normalize_title(title: str) -> str:
    """Lowercase + collapse whitespace + strip non-word chars for fuzzy matching."""
    return re.sub(r"\W+", " ", title or "").strip().lower()


def _fetch_spotify_metadata(url: str) -> Optional[dict]:
    """Scrape the public Spotify episode page for episode title and show name."""
    try:
        r = requests.get(
            url,
            headers={"User-Agent": _OG_USER_AGENT},
            timeout=_HTTP_TIMEOUT,
            allow_redirects=True,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log.warning("[spotify] OG fetch failed url=%s err=%s", url, e)
        return None

    title_match = _OG_TITLE_RE.search(r.text)
    desc_match = _OG_DESC_RE.search(r.text)
    if not title_match:
        log.warning("[spotify] no og:title in page url=%s", url)
        return None

    episode_title = title_match.group(1).strip()
    # Spotify formats og:description as "<Show Name> · Episode" (or "· Podcast"
    # depending on locale). Take the part before the middle dot as the show.
    show_name = ""
    if desc_match:
        raw_desc = desc_match.group(1)
        show_name = raw_desc.split("·")[0].strip()  # · = U+00B7

    return {"episode_title": episode_title, "show_name": show_name}


def _find_feed_url_via_itunes(show_name: str) -> Optional[str]:
    """Search iTunes for the podcast and return its RSS feed URL."""
    if not show_name:
        return None
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": show_name, "entity": "podcast", "limit": 5},
            timeout=_HTTP_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        log.warning("[spotify] iTunes search failed show=%s err=%s", show_name, e)
        return None

    target = _normalize_title(show_name)
    for result in data.get("results", []):
        feed = result.get("feedUrl")
        if not feed:
            continue
        # Prefer an exact normalized match on the show name; fall back to first
        # result with a feed if nothing matches exactly.
        if _normalize_title(result.get("collectionName", "")) == target:
            return feed
    for result in data.get("results", []):
        if result.get("feedUrl"):
            log.info(
                "[spotify] iTunes fuzzy match show=%s -> %s",
                show_name,
                result.get("collectionName"),
            )
            return result["feedUrl"]
    return None


def _find_episode_in_feed(feed_url: str, episode_title: str) -> Optional[str]:
    """Parse the RSS feed and return the enclosure URL for the matching episode."""
    try:
        r = requests.get(
            feed_url,
            headers={"User-Agent": _DEFAULT_USER_AGENT},
            timeout=_HTTP_TIMEOUT,
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except (requests.RequestException, ET.ParseError) as e:
        log.warning("[spotify] feed fetch/parse failed feed=%s err=%s", feed_url, e)
        return None

    target = _normalize_title(episode_title)
    fallback = None
    for item in root.iter("item"):
        item_title = (item.findtext("title") or "").strip()
        enclosure = item.find("enclosure")
        if enclosure is None:
            continue
        url = enclosure.get("url")
        if not url:
            continue
        norm = _normalize_title(item_title)
        if norm == target:
            return url
        # Substring match in either direction handles "(Trailer)" suffixes,
        # numeric episode prefixes, etc.
        if target and (target in norm or norm in target) and fallback is None:
            fallback = url
    return fallback


def resolve_spotify_url(url: str) -> Optional[str]:
    """Resolve a Spotify episode URL to a public RSS audio enclosure URL.

    Returns ``None`` when the episode cannot be resolved (Spotify Originals,
    show not on iTunes, title mismatch, network failure). Callers should
    surface a Spotify-specific error message in that case.
    """
    if not is_spotify_episode_url(url):
        return None

    meta = _fetch_spotify_metadata(url)
    if not meta or not meta.get("episode_title"):
        return None

    feed = _find_feed_url_via_itunes(meta.get("show_name", ""))
    if not feed:
        log.info(
            "[spotify] no feed found show=%s episode=%s",
            meta.get("show_name"),
            meta["episode_title"],
        )
        return None

    audio = _find_episode_in_feed(feed, meta["episode_title"])
    if not audio:
        log.info(
            "[spotify] episode not in feed feed=%s title=%s",
            feed,
            meta["episode_title"],
        )
        return None

    log.info(
        "[spotify] resolved %s -> %s (via %s)",
        url,
        urlparse(audio).netloc,
        urlparse(feed).netloc,
    )
    return audio
