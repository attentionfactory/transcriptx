import base64
import importlib
import json
import os
import sys
import tempfile
import types
import unittest


def _reload_modules(db_path):
    os.environ["DB_PATH"] = db_path
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["POLAR_WEBHOOK_SECRET"] = "whsec_" + base64.b64encode(b"k").decode()
    os.environ["POLAR_STARTER_PRODUCT_ID"] = "prod_starter"
    os.environ["POLAR_PRO_PRODUCT_ID"] = "prod_pro"

    for mod in ("app", "database", "transcribe"):
        if mod in sys.modules:
            del sys.modules[mod]

    if "disposable_email_domains" not in sys.modules:
        sys.modules["disposable_email_domains"] = types.SimpleNamespace(blocklist=set())
    if "groq" not in sys.modules:
        class _FakeGroq:
            def __init__(self, *args, **kwargs):
                pass
        sys.modules["groq"] = types.SimpleNamespace(Groq=_FakeGroq)

    database = importlib.import_module("database")
    transcribe = importlib.import_module("transcribe")
    app_module = importlib.import_module("app")
    return app_module, database, transcribe


class ClassifyErrorTests(unittest.TestCase):
    """The error classifier is pure — test it directly without the Flask app."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        _, _, self.transcribe = _reload_modules(self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_user_input_markers(self):
        for msg in (
            "No video found at this URL.",
            "This video is private",
            "Video unavailable",
            "Removed by the uploader",
            "Audio too large (40MB, max 25MB)",
            "Unsupported URL: example.com",
        ):
            self.assertEqual(
                self.transcribe.classify_error(msg), "user_input", f"missed: {msg!r}"
            )

    def test_upstream_default(self):
        for msg in (
            "Audio download failed: HTTP 500",
            "Timed out fetching video info",
            "YouTube anti-bot check blocked this request (HTTP 429 / LOGIN_REQUIRED)",
            "RuntimeError: Connection reset by peer",
            "",
            None,
        ):
            self.assertEqual(
                self.transcribe.classify_error(msg), "upstream", f"miscategorized: {msg!r}"
            )


class RefundBranchTests(unittest.TestCase):
    """End-to-end via /api/extract — credit accounting depends on error_kind."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database, _ = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()

        self.user_id = self.database.create_user("u@example.com", "hash")
        self.assertIsNotNone(self.user_id)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _login(self):
        user = self.database.get_user_by_id(self.user_id)
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["pwd_changed_at"] = user.get("password_changed_at") or ""

    def _credits_used(self):
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT credits_used FROM users WHERE id = ?", (self.user_id,)
            ).fetchone()
            return row["credits_used"]

    def _last_log_status(self):
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT status FROM transcript_logs ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row["status"] if row else None

    def _post(self):
        return self.client.post(
            "/api/extract",
            data=json.dumps({"url": "https://youtu.be/abc"}),
            content_type="application/json",
        )

    def test_user_input_error_keeps_credit(self):
        """Private/unsupported video: charged 1 credit, log = error_user_input."""
        self._login()
        self.app_module.process_url = lambda url, model="", language=None: {
            "url": url,
            "status": "error",
            "error": "This video is private",
            "error_kind": "user_input",
        }

        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["status"], "error")
        self.assertTrue(body.get("credit_kept"))
        self.assertEqual(self._credits_used(), 1)
        self.assertEqual(self._last_log_status(), "error_user_input")

    def test_upstream_error_refunds_credit(self):
        """Network/Groq failure: refunded, log = error, no credit_kept flag."""
        self._login()
        self.app_module.process_url = lambda url, model="", language=None: {
            "url": url,
            "status": "error",
            "error": "Audio download failed: HTTP 500",
            "error_kind": "upstream",
        }

        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["status"], "error")
        self.assertFalse(body.get("credit_kept"))
        self.assertEqual(self._credits_used(), 0)
        self.assertEqual(self._last_log_status(), "error")

    def test_unknown_error_kind_treated_as_upstream(self):
        """Defensive: missing error_kind should refund (err on the user's side)."""
        self._login()
        self.app_module.process_url = lambda url, model="", language=None: {
            "url": url,
            "status": "error",
            "error": "Something went wrong",
        }

        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._credits_used(), 0)
        self.assertEqual(self._last_log_status(), "error")


if __name__ == "__main__":
    unittest.main()
