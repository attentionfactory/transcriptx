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


class _ExtractTestBase(unittest.TestCase):
    """Shared setup: stub process_url, create + login a user, make requests."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database, self.transcribe = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()

        self.user_id = self.database.create_user("u@example.com", "hash")
        self.assertIsNotNone(self.user_id)
        # Record each process_url call so tests can assert on the args.
        self.calls = []

        def fake_process_url(url, model="whisper-large-v3-turbo", language=None):
            self.calls.append({"url": url, "model": model, "language": language})
            return {
                "url": url,
                "status": "success",
                "transcript": "hello",
                "language": language or "en",  # pretend Whisper detected this
                "segments": [],
                "words": [],
            }

        self.app_module.process_url = fake_process_url

    def tearDown(self):
        self.tmpdir.cleanup()

    def _login(self):
        user = self.database.get_user_by_id(self.user_id)
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["pwd_changed_at"] = user.get("password_changed_at") or ""

    def _extract(self, **body):
        body.setdefault("url", "https://youtu.be/abc")
        return self.client.post(
            "/api/extract",
            data=json.dumps(body),
            content_type="application/json",
        )


class LanguageParamTests(_ExtractTestBase):
    def test_auto_detect_when_language_omitted(self):
        self._login()
        resp = self._extract()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(self.calls[0]["language"], "omitted language should be None (auto)")

    def test_explicit_language_is_passed_through(self):
        self._login()
        resp = self._extract(language="en")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.calls[0]["language"], "en")

    def test_empty_string_language_means_auto(self):
        self._login()
        resp = self._extract(language="")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(self.calls[0]["language"])

    def test_auto_string_means_auto(self):
        self._login()
        resp = self._extract(language="auto")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(self.calls[0]["language"])

    def test_invalid_language_code_rejected(self):
        self._login()
        for bad in ("xx", "123", "eng", "english"):
            resp = self._extract(language=bad)
            self.assertEqual(resp.status_code, 400, f"language={bad!r} should 400")
        self.assertEqual(len(self.calls), 0, "no transcription should have run")

    def test_case_insensitive_language(self):
        self._login()
        resp = self._extract(language="EN")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.calls[0]["language"], "en")

    def test_requested_and_detected_language_persisted(self):
        self._login()
        self._extract(language="ms")  # user asked for Malay
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT requested_language, detected_language FROM transcript_logs "
                "WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (self.user_id,),
            ).fetchone()
        self.assertEqual(row["requested_language"], "ms")
        # The stub echoes language back as "detected", so this should be "ms" too.
        self.assertEqual(row["detected_language"], "ms")


class RetryTranscriptTests(_ExtractTestBase):
    def _insert_success_log(self, user_id=None, url="https://youtu.be/abc", detected="ms"):
        """Directly insert a successful log we can retry."""
        return self.database.log_transcript_attempt(
            user_id if user_id is not None else self.user_id,
            "u@example.com",
            url,
            "success",
            credits_used=1,
            requested_language=None,
            detected_language=detected,
        )

    def test_requires_auth(self):
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": 1, "language": "en"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_happy_path_reruns_without_credit(self):
        self._login()
        log_id = self._insert_success_log()
        before = self._credits_used()

        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id, "language": "en"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["status"], "success")
        self.assertTrue(body.get("retried"))
        self.assertEqual(body["language"], "en")

        # No credit charged.
        self.assertEqual(self._credits_used(), before)
        # process_url called with language="en".
        self.assertEqual(self.calls[-1]["language"], "en")
        # retried_at is now set.
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT retried_at FROM transcript_logs WHERE id = ?", (log_id,)
            ).fetchone()
        self.assertIsNotNone(row["retried_at"])

    def test_second_retry_rejected(self):
        self._login()
        log_id = self._insert_success_log()
        self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id, "language": "en"}),
            content_type="application/json",
        )
        # Second call on same log should 403.
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id, "language": "en"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_cannot_retry_other_users_log(self):
        other_id = self.database.create_user("b@example.com", "hash")
        other_log = self._insert_success_log(user_id=other_id)

        self._login()
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": other_log, "language": "en"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_invalid_language_rejected(self):
        self._login()
        log_id = self._insert_success_log()
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id, "language": "xx"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_missing_language_rejected(self):
        self._login()
        log_id = self._insert_success_log()
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_cannot_retry_failed_log(self):
        self._login()
        # Insert a failed log directly via the helper.
        log_id = self.database.log_transcript_attempt(
            self.user_id, "u@example.com", "https://youtu.be/x",
            "error", credits_used=0,
        )
        resp = self.client.post(
            "/api/retranscribe",
            data=json.dumps({"log_id": log_id, "language": "en"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def _credits_used(self):
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT credits_used FROM users WHERE id = ?", (self.user_id,)
            ).fetchone()
            return row["credits_used"]


if __name__ == "__main__":
    unittest.main()
