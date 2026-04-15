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

    for mod in ("app", "database"):
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
    app_module = importlib.import_module("app")
    return app_module, database


class TranscriptRatingTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()

        self.user_a = self.database.create_user("a@example.com", "hash-a")
        self.user_b = self.database.create_user("b@example.com", "hash-b")
        self.assertIsNotNone(self.user_a)
        self.assertIsNotNone(self.user_b)

        self.log_a = self.database.log_transcript_attempt(
            self.user_a, "a@example.com", "https://youtu.be/a", "success", credits_used=1
        )
        self.log_b = self.database.log_transcript_attempt(
            self.user_b, "b@example.com", "https://youtu.be/b", "success", credits_used=1
        )
        self.assertIsInstance(self.log_a, int)
        self.assertIsInstance(self.log_b, int)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _login_as(self, user_id):
        user = self.database.get_user_by_id(user_id)
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["pwd_changed_at"] = user.get("password_changed_at") or ""

    def _get_rating(self, log_id):
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT rating FROM transcript_logs WHERE id = ?", (log_id,)
            ).fetchone()
            return row["rating"] if row else None

    def test_requires_auth(self):
        resp = self.client.post(
            "/api/rate-transcript",
            data=json.dumps({"log_id": self.log_a, "rating": 1}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_user_can_rate_own_transcript(self):
        self._login_as(self.user_a)
        resp = self.client.post(
            "/api/rate-transcript",
            data=json.dumps({"log_id": self.log_a, "rating": 1}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")
        self.assertEqual(self._get_rating(self.log_a), 1)

    def test_user_cannot_rate_other_users_transcript(self):
        self._login_as(self.user_b)
        resp = self.client.post(
            "/api/rate-transcript",
            data=json.dumps({"log_id": self.log_a, "rating": -1}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIsNone(self._get_rating(self.log_a))

    def test_invalid_rating_value_rejected(self):
        self._login_as(self.user_a)
        for bad in (0, 5, -2, "good"):
            resp = self.client.post(
                "/api/rate-transcript",
                data=json.dumps({"log_id": self.log_a, "rating": bad}),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 400, f"bad={bad!r} should 400")
        self.assertIsNone(self._get_rating(self.log_a))

    def test_rating_overwrites_previous(self):
        self._login_as(self.user_a)
        for rating in (1, -1):
            resp = self.client.post(
                "/api/rate-transcript",
                data=json.dumps({"log_id": self.log_a, "rating": rating}),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._get_rating(self.log_a), -1)

    def test_missing_fields_rejected(self):
        self._login_as(self.user_a)
        resp = self.client.post(
            "/api/rate-transcript",
            data=json.dumps({"log_id": self.log_a}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
