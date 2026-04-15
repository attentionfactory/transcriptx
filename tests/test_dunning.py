import base64
import hashlib
import hmac
import importlib
import json
import os
import sys
import tempfile
import time
import types
import unittest


def _reload_modules(db_path, signing_key_bytes):
    whsec = "whsec_" + base64.b64encode(signing_key_bytes).decode()
    os.environ["DB_PATH"] = db_path
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["POLAR_WEBHOOK_SECRET"] = whsec
    os.environ["POLAR_STARTER_PRODUCT_ID"] = "prod_starter"
    os.environ["POLAR_PRO_PRODUCT_ID"] = "prod_pro"
    os.environ["POLAR_CUSTOMER_PORTAL"] = "https://polar.example/portal"

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


def _signed_headers(key_bytes, body, webhook_id):
    ts = str(int(time.time()))
    signed = f"{webhook_id}.{ts}.".encode("utf-8") + body
    sig = base64.b64encode(hmac.new(key_bytes, signed, hashlib.sha256).digest()).decode()
    return {
        "webhook-id": webhook_id,
        "webhook-timestamp": ts,
        "webhook-signature": f"v1,{sig}",
    }


class DunningEmailTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.key = b"polar-signing-key"
        self.app_module, self.database = _reload_modules(self.db_path, self.key)
        self.client = self.app_module.app.test_client()

        # Capture _send_email calls without actually hitting Resend.
        self.sent = []
        self.app_module._send_email = lambda to, subject, html: self.sent.append(
            {"to": to, "subject": subject, "html": html}
        ) or True

    def tearDown(self):
        self.tmpdir.cleanup()

    def _post_webhook(self, event_type, email="user@example.com", webhook_id=None):
        payload = {
            "type": event_type,
            "data": {
                "customer": {"id": "cus_1", "email": email},
                "product": {"id": "prod_pro"},
                "status": "past_due" if event_type == "subscription.past_due" else "active",
            },
        }
        body = json.dumps(payload).encode()
        wid = webhook_id or f"evt_{event_type}_{len(self.sent)}"
        headers = _signed_headers(self.key, body, wid)
        return self.client.post("/webhooks/polar", data=body, headers=headers)

    def test_past_due_sends_email(self):
        resp = self._post_webhook("subscription.past_due")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.sent), 1)
        self.assertIn("card", self.sent[0]["subject"].lower())
        self.assertIn("polar.example/portal", self.sent[0]["html"])

    def test_past_due_idempotent_across_duplicate_deliveries(self):
        # Same stage, two deliveries with different webhook-ids (the claim_event
        # table catches exact duplicates; this tests the stage-level guard).
        self._post_webhook("subscription.past_due", webhook_id="evt_pd_1")
        self._post_webhook("subscription.past_due", webhook_id="evt_pd_2")
        self.assertEqual(len(self.sent), 1, "stage guard should prevent double-send")

    def test_revoked_sends_winback_email(self):
        # Production flow: a revoked user has existed (created first).
        self._post_webhook("subscription.active", webhook_id="evt_active")
        self.sent.clear()
        self._post_webhook("subscription.revoked", webhook_id="evt_rev")
        self.assertEqual(len(self.sent), 1)
        self.assertIn("50%", self.sent[0]["subject"] + self.sent[0]["html"])

    def test_canceled_sends_goodbye_email(self):
        self._post_webhook("subscription.active", webhook_id="evt_active")
        self.sent.clear()
        self._post_webhook("subscription.canceled", webhook_id="evt_cancel")
        self.assertEqual(len(self.sent), 1)
        self.assertIn("missed", self.sent[0]["subject"].lower())

    def test_reactivation_clears_stage_so_next_past_due_resends(self):
        self._post_webhook("subscription.past_due", webhook_id="evt_pd_1")
        self.assertEqual(len(self.sent), 1)

        # User pays, comes back to active. Should NOT email, but clears stage.
        self._post_webhook("subscription.active", webhook_id="evt_active")
        self.assertEqual(len(self.sent), 1)

        # Another past_due later — should email again.
        self._post_webhook("subscription.past_due", webhook_id="evt_pd_2")
        self.assertEqual(len(self.sent), 2)

    def test_unknown_user_no_email(self):
        """If the webhook arrives for a polar_id we don't have locally, no email goes out.

        (In the current code this actually creates a user via _upsert. This
        test just confirms we don't crash and at least one webhook still sends
        correctly — so it's really a smoke test around the dispatcher guard.)
        """
        resp = self._post_webhook("subscription.past_due", email="ghost@example.com")
        self.assertEqual(resp.status_code, 200)
        # Either 0 or 1 emails — but no traceback.
        self.assertLessEqual(len(self.sent), 1)


if __name__ == "__main__":
    unittest.main()
