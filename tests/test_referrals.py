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


class ReferralCodeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()
        # Silence OTP/email sends.
        self.app_module._send_email = lambda *a, **kw: True
        self.app_module._send_otp_email = lambda *a, **kw: True

    def tearDown(self):
        self.tmpdir.cleanup()

    def _login(self, user_id):
        user = self.database.get_user_by_id(user_id)
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["pwd_changed_at"] = user.get("password_changed_at") or ""

    def _credits_used(self, user_id):
        with self.database.get_db() as db:
            row = db.execute("SELECT credits_used FROM users WHERE id = ?", (user_id,)).fetchone()
            return row["credits_used"]

    def test_code_is_stable_and_unique_per_user(self):
        a = self.database.create_user("a@example.com", "h")
        b = self.database.create_user("b@example.com", "h")
        code_a = self.database.get_or_create_referral_code(a)
        code_b = self.database.get_or_create_referral_code(b)
        # Stable across calls.
        self.assertEqual(code_a, self.database.get_or_create_referral_code(a))
        self.assertEqual(len(code_a), self.database.REFERRAL_CODE_LENGTH)
        self.assertNotEqual(code_a, code_b)

    def test_api_me_referral_requires_auth(self):
        resp = self.client.get("/api/me/referral")
        self.assertEqual(resp.status_code, 401)

    def test_api_me_referral_returns_code_and_stats(self):
        user_id = self.database.create_user("u@example.com", "h")
        self._login(user_id)
        resp = self.client.get("/api/me/referral")
        self.assertEqual(resp.status_code, 200)
        d = resp.get_json()
        self.assertEqual(d["status"], "ok")
        self.assertTrue(d["code"])
        self.assertEqual(d["referred_count"], 0)
        self.assertEqual(d["credits_earned"], 0)
        self.assertEqual(d["reward_per_referral"], 10)


class ReferralSignupTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()
        self.app_module._send_email = lambda *a, **kw: True
        self.app_module._send_otp_email = lambda *a, **kw: True

        # Pre-existing referrer with a known code.
        self.referrer_id = self.database.create_user("ref@example.com", "h")
        self.ref_code = self.database.get_or_create_referral_code(self.referrer_id)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _signup(self, email, password="longenough", code=None):
        body = {"email": email, "password": password}
        if code is not None:
            body["referral_code"] = code
        return self.client.post(
            "/api/signup",
            data=json.dumps(body),
            content_type="application/json",
        )

    def _credits_used(self, user_id):
        with self.database.get_db() as db:
            row = db.execute("SELECT credits_used FROM users WHERE id = ?", (user_id,)).fetchone()
            return row["credits_used"] if row else None

    def _referred_by(self, email):
        with self.database.get_db() as db:
            row = db.execute("SELECT referred_by FROM users WHERE email = ?", (email,)).fetchone()
            return row["referred_by"] if row else None

    def test_signup_with_valid_code_sets_referred_by_and_grants_credits(self):
        resp = self._signup("new@example.com", code=self.ref_code)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._referred_by("new@example.com"), self.referrer_id)

        # Referee got +20 — credits_used goes negative (the ledger's "bank").
        new_user = self.database.get_user_by_email("new@example.com")
        self.assertEqual(self._credits_used(new_user["id"]), -10)

    def test_signup_with_invalid_code_is_silently_ignored(self):
        resp = self._signup("nobody@example.com", code="BOGUS123")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(self._referred_by("nobody@example.com"))
        new_user = self.database.get_user_by_email("nobody@example.com")
        self.assertEqual(self._credits_used(new_user["id"]), 0)

    def test_self_referral_rejected_by_email_match(self):
        # Someone tries to use their own referral code when signing up — blocked.
        resp = self._signup("ref@example.com", code=self.ref_code)
        # ref@example.com already exists (unverified), so the re-signup branch
        # runs. Apply should no-op because email matches the referrer.
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(self._referred_by("ref@example.com"))

    def test_signup_without_code_is_plain_signup(self):
        resp = self._signup("plain@example.com")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(self._referred_by("plain@example.com"))


class ReferralPayoutTests(unittest.TestCase):
    """Referrer is paid on the referee's first successful /api/extract."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()
        self.app_module._send_email = lambda *a, **kw: True
        self.app_module._send_otp_email = lambda *a, **kw: True

        self.referrer_id = self.database.create_user("ref@example.com", "h")
        self.database.get_or_create_referral_code(self.referrer_id)
        self.referee_id = self.database.create_user("ree@example.com", "h")
        self.database.set_referred_by(self.referee_id, self.referrer_id)

        # Stub process_url to return a successful transcription.
        self.app_module.process_url = lambda url, model="", language=None: {
            "url": url,
            "status": "success",
            "transcript": "hello",
            "language": "en",
            "segments": [],
            "words": [],
        }

    def tearDown(self):
        self.tmpdir.cleanup()

    def _login(self, user_id):
        user = self.database.get_user_by_id(user_id)
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["pwd_changed_at"] = user.get("password_changed_at") or ""

    def _credits_used(self, user_id):
        with self.database.get_db() as db:
            row = db.execute("SELECT credits_used FROM users WHERE id = ?", (user_id,)).fetchone()
            return row["credits_used"]

    def _extract(self):
        return self.client.post(
            "/api/extract",
            data=json.dumps({"url": "https://youtu.be/abc"}),
            content_type="application/json",
        )

    def test_first_success_pays_referrer_and_marks_paid(self):
        self._login(self.referee_id)
        before = self._credits_used(self.referrer_id)
        resp = self._extract()
        self.assertEqual(resp.status_code, 200)

        after = self._credits_used(self.referrer_id)
        self.assertEqual(after, before - 10, "referrer should get +10 (credits_used -= 10)")

        with self.database.get_db() as db:
            row = db.execute(
                "SELECT referral_credit_paid FROM users WHERE id = ?", (self.referee_id,)
            ).fetchone()
        self.assertEqual(row["referral_credit_paid"], 1)

    def test_second_success_does_not_pay_again(self):
        self._login(self.referee_id)
        self._extract()
        mid = self._credits_used(self.referrer_id)
        self._extract()
        after = self._credits_used(self.referrer_id)
        self.assertEqual(after, mid, "second extract must not re-pay")

    def test_no_payout_when_referee_has_no_referrer(self):
        orphan_id = self.database.create_user("orphan@example.com", "h")
        self._login(orphan_id)
        before = self._credits_used(self.referrer_id)
        resp = self._extract()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._credits_used(self.referrer_id), before)

    def test_lifetime_cap_stops_payout(self):
        """After ``cap / reward`` paid referrals, further referees don't pay out.

        The cap is measured in referrals-paid × reward_credits, not in the
        referrer's credit balance (which is a separate ledger).
        """
        cap = self.database.REFERRAL_MAX_CREDITS_PER_REFERRER
        reward = self.database.REFERRAL_REWARD_CREDITS
        max_paid = cap // reward  # how many referrals can be paid at most

        # Fabricate (max_paid) prior paid referrals to simulate the cap.
        with self.database.get_db() as db:
            for i in range(max_paid):
                db.execute(
                    "INSERT INTO users (email, password_hash, referred_by, referral_credit_paid) "
                    "VALUES (?, 'h', ?, 1)",
                    (f"prior{i}@example.com", self.referrer_id),
                )

        # The already-set-up referee runs their first extract — should NOT pay
        # the referrer because the cap is already met.
        self._login(self.referee_id)
        before = self._credits_used(self.referrer_id)
        resp = self._extract()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            self._credits_used(self.referrer_id), before,
            "referrer must not exceed lifetime cap"
        )


if __name__ == "__main__":
    unittest.main()
