"""Tests for spotify_resolver.

The network-touching path is exercised against mocked HTTP responses so the
suite stays offline-safe. One opt-in live test (skipped by default) hits the
real iTunes API to catch upstream changes.
"""

import os
import sys
import unittest
from unittest import mock

# Make repo root importable when running `python -m unittest` from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import spotify_resolver  # noqa: E402


SPOTIFY_PAGE_HTML = """
<!doctype html>
<html><head>
<meta property="og:title" content="A Masterclass in Brand Longevity, Global Growth and Becoming a Category Leader | Jackie Widmann of BERO Brewing"/>
<meta property="og:description" content="Marketing Happy Hour · Episode"/>
<meta property="og:audio" content="https://p.scdn.co/mp3-preview/abc.mp3"/>
</head><body>not the audio</body></html>
"""

ITUNES_RESPONSE = {
    "results": [
        {"collectionName": "Marketing Happy Hour", "feedUrl": "https://example.com/mhh.rss"},
        {"collectionName": "Other Show", "feedUrl": "https://example.com/other.rss"},
    ]
}

RSS_FEED_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Marketing Happy Hour</title>
    <item>
      <title>Some Other Episode</title>
      <enclosure url="https://cdn.example.com/other.mp3" type="audio/mpeg"/>
    </item>
    <item>
      <title>A Masterclass in Brand Longevity, Global Growth and Becoming a Category Leader | Jackie Widmann of BERO Brewing</title>
      <enclosure url="https://cdn.example.com/jackie.mp3" type="audio/mpeg"/>
    </item>
  </channel>
</rss>
"""


def _mock_response(*, text=None, content=None, json_data=None, status=200):
    m = mock.Mock()
    m.status_code = status
    m.text = text or ""
    m.content = content if content is not None else (text or "").encode("utf-8")
    m.json = mock.Mock(return_value=json_data or {})
    m.raise_for_status = mock.Mock()
    return m


class TestUrlDetection(unittest.TestCase):
    def test_recognizes_open_spotify_episode(self):
        self.assertTrue(
            spotify_resolver.is_spotify_episode_url(
                "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
            )
        )

    def test_recognizes_locale_prefixed_episode(self):
        self.assertTrue(
            spotify_resolver.is_spotify_episode_url(
                "https://open.spotify.com/intl-de/episode/2Lj3136eZnAhC0wF662pW5"
            )
        )

    def test_rejects_show_url(self):
        self.assertFalse(
            spotify_resolver.is_spotify_episode_url(
                "https://open.spotify.com/show/abc123"
            )
        )

    def test_rejects_youtube(self):
        self.assertFalse(
            spotify_resolver.is_spotify_episode_url("https://youtube.com/watch?v=x")
        )

    def test_rejects_empty(self):
        self.assertFalse(spotify_resolver.is_spotify_episode_url(""))
        self.assertFalse(spotify_resolver.is_spotify_episode_url(None))


class TestNormalize(unittest.TestCase):
    def test_collapses_whitespace_and_punctuation(self):
        self.assertEqual(
            spotify_resolver._normalize_title("Hello,   World! (Trailer)"),
            "hello world trailer",
        )

    def test_handles_empty(self):
        self.assertEqual(spotify_resolver._normalize_title(""), "")
        self.assertEqual(spotify_resolver._normalize_title(None), "")


class TestEndToEndResolve(unittest.TestCase):
    def test_happy_path(self):
        def fake_get(url, **kwargs):
            if url.startswith("https://open.spotify.com/"):
                return _mock_response(text=SPOTIFY_PAGE_HTML)
            if url == "https://itunes.apple.com/search":
                return _mock_response(json_data=ITUNES_RESPONSE)
            if url == "https://example.com/mhh.rss":
                return _mock_response(content=RSS_FEED_XML)
            raise AssertionError("unexpected url " + url)

        with mock.patch.object(spotify_resolver.requests, "get", side_effect=fake_get):
            result = spotify_resolver.resolve_spotify_url(
                "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
            )

        self.assertEqual(result, "https://cdn.example.com/jackie.mp3")

    def test_returns_none_when_show_not_in_itunes(self):
        def fake_get(url, **kwargs):
            if url.startswith("https://open.spotify.com/"):
                return _mock_response(text=SPOTIFY_PAGE_HTML)
            if url == "https://itunes.apple.com/search":
                return _mock_response(json_data={"results": []})
            raise AssertionError("unexpected url " + url)

        with mock.patch.object(spotify_resolver.requests, "get", side_effect=fake_get):
            result = spotify_resolver.resolve_spotify_url(
                "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
            )
        self.assertIsNone(result)

    def test_returns_none_when_episode_not_in_feed(self):
        empty_feed = b"""<?xml version="1.0"?><rss><channel></channel></rss>"""

        def fake_get(url, **kwargs):
            if url.startswith("https://open.spotify.com/"):
                return _mock_response(text=SPOTIFY_PAGE_HTML)
            if url == "https://itunes.apple.com/search":
                return _mock_response(json_data=ITUNES_RESPONSE)
            if url == "https://example.com/mhh.rss":
                return _mock_response(content=empty_feed)
            raise AssertionError("unexpected url " + url)

        with mock.patch.object(spotify_resolver.requests, "get", side_effect=fake_get):
            result = spotify_resolver.resolve_spotify_url(
                "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
            )
        self.assertIsNone(result)

    def test_substring_match_finds_episode_with_extra_decoration(self):
        feed_with_decoration = b"""<?xml version="1.0"?>
<rss><channel>
  <item>
    <title>EP 142: A Masterclass in Brand Longevity, Global Growth and Becoming a Category Leader | Jackie Widmann of BERO Brewing</title>
    <enclosure url="https://cdn.example.com/decorated.mp3" type="audio/mpeg"/>
  </item>
</channel></rss>"""

        def fake_get(url, **kwargs):
            if url.startswith("https://open.spotify.com/"):
                return _mock_response(text=SPOTIFY_PAGE_HTML)
            if url == "https://itunes.apple.com/search":
                return _mock_response(json_data=ITUNES_RESPONSE)
            if url == "https://example.com/mhh.rss":
                return _mock_response(content=feed_with_decoration)
            raise AssertionError("unexpected url " + url)

        with mock.patch.object(spotify_resolver.requests, "get", side_effect=fake_get):
            result = spotify_resolver.resolve_spotify_url(
                "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
            )
        self.assertEqual(result, "https://cdn.example.com/decorated.mp3")

    def test_returns_none_for_non_spotify_url(self):
        result = spotify_resolver.resolve_spotify_url("https://youtube.com/watch?v=x")
        self.assertIsNone(result)


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_SPOTIFY_TEST"),
    "set RUN_LIVE_SPOTIFY_TEST=1 to hit the real Spotify + iTunes APIs",
)
class TestLive(unittest.TestCase):
    """Optional smoke test against live upstream services. Skipped by default."""

    def test_resolves_known_episode(self):
        url = spotify_resolver.resolve_spotify_url(
            "https://open.spotify.com/episode/2Lj3136eZnAhC0wF662pW5"
        )
        self.assertIsNotNone(url, "live resolver returned None — upstream may have changed")
        self.assertIn(".mp3", url.lower())


if __name__ == "__main__":
    unittest.main()
