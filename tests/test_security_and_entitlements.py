import base64
import hashlib
import hmac
import importlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
import types
import time


def _reload_modules(db_path, webhook_secret):
    os.environ["DB_PATH"] = db_path
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["POLAR_WEBHOOK_SECRET"] = webhook_secret
    os.environ["POLAR_STARTER_PRODUCT_ID"] = "prod_starter"
    os.environ["POLAR_PRO_PRODUCT_ID"] = "prod_pro"

    for mod in ("app", "database"):
        if mod in sys.modules:
            del sys.modules[mod]

    # Test environment stubs for optional runtime dependencies.
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


def _signed_headers(secret_key_bytes, body, webhook_id="evt_1", ts=None):
    if ts is None:
        ts = str(int(time.time()))
    signed = f"{webhook_id}.{ts}.".encode("utf-8") + body
    sig = base64.b64encode(hmac.new(secret_key_bytes, signed, hashlib.sha256).digest()).decode("utf-8")
    return {
        "webhook-id": webhook_id,
        "webhook-timestamp": ts,
        "webhook-signature": f"v1,{sig}",
    }


class SecurityAndEntitlementsTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.signing_key = b"polar-test-signing-key"
        self.whsec = "whsec_" + base64.b64encode(self.signing_key).decode("utf-8")
        self.app_module, self.database = _reload_modules(self.db_path, self.whsec)
        self.client = self.app_module.app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_webhook_rejects_invalid_signature(self):
        payload = {
            "type": "subscription.created",
            "data": {
                "customer": {"id": "cus_1", "email": "user@example.com"},
                "product": {"id": "prod_pro"},
                "status": "active",
            },
        }
        body = json.dumps(payload).encode("utf-8")
        resp = self.client.post(
            "/webhooks/polar",
            data=body,
            headers={
                "webhook-id": "evt_invalid",
                "webhook-timestamp": str(int(time.time())),
                "webhook-signature": "v1,invalidsig",
            },
        )
        self.assertEqual(resp.status_code, 401)

    def test_webhook_valid_signature_and_idempotency(self):
        payload = {
            "type": "subscription.active",
            "data": {
                "customer": {"id": "cus_2", "email": "pro@example.com"},
                "product": {"id": "prod_pro"},
                "status": "active",
            },
        }
        body = json.dumps(payload).encode("utf-8")
        headers = _signed_headers(self.signing_key, body, webhook_id="evt_dupe")

        first = self.client.post("/webhooks/polar", data=body, headers=headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["status"], "ok")

        second = self.client.post("/webhooks/polar", data=body, headers=headers)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.get_json().get("message"), "duplicate")

        user = self.database.get_user_by_email("pro@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user["plan"], "pro")

    def test_unknown_product_is_ignored_for_strict_events(self):
        payload = {
            "type": "subscription.created",
            "data": {
                "customer": {"id": "cus_3", "email": "unknown@example.com"},
                "product": {"id": "not_configured"},
                "status": "active",
            },
        }
        body = json.dumps(payload).encode("utf-8")
        headers = _signed_headers(self.signing_key, body, webhook_id="evt_unknown")
        resp = self.client.post("/webhooks/polar", data=body, headers=headers)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("status"), "ignored")
        self.assertIsNone(self.database.get_user_by_email("unknown@example.com"))

    def test_login_rate_limit_blocks_excessive_attempts(self):
        last_status = None
        for _ in range(16):
            resp = self.client.post("/api/login", json={"email": "", "password": ""})
            last_status = resp.status_code
        self.assertEqual(last_status, 429)

    def test_effective_entitlement_for_past_due_grace(self):
        user_id = self.database.create_user("grace@example.com", "hash")
        self.assertIsNotNone(user_id)

        future = (datetime.utcnow() + timedelta(days=2)).isoformat()
        with self.database.get_db() as db:
            db.execute(
                "UPDATE users SET plan='starter', billing_state='past_due', grace_until=? WHERE id=?",
                (future, user_id),
            )
        user = self.database.get_user_by_id(user_id)
        ent = self.database.effective_entitlement(user)
        self.assertEqual(ent["effective_plan"], "starter")
        self.assertTrue(ent["has_paid_access"])

        past = (datetime.utcnow() - timedelta(days=1)).isoformat()
        with self.database.get_db() as db:
            db.execute("UPDATE users SET grace_until=? WHERE id=?", (past, user_id))
        user = self.database.get_user_by_id(user_id)
        ent = self.database.effective_entitlement(user)
        self.assertEqual(ent["effective_plan"], "free")
        self.assertFalse(ent["has_paid_access"])

    def test_sync_webhook_past_due_then_revoked(self):
        future = (datetime.utcnow() + timedelta(days=3)).isoformat()
        self.database.sync_polar_subscription_webhook(
            "subscription.past_due",
            {
                "customer": {"id": "cus_4", "email": "billing@example.com"},
                "current_period_end": future,
            },
            "pro",
        )
        user = self.database.get_user_by_email("billing@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user["billing_state"], "past_due")
        self.assertEqual(self.database.effective_entitlement(user)["effective_plan"], "pro")

        self.database.sync_polar_subscription_webhook(
            "subscription.revoked",
            {"customer": {"id": "cus_4", "email": "billing@example.com"}},
            "pro",
        )
        user = self.database.get_user_by_email("billing@example.com")
        self.assertEqual(user["plan"], "free")
        self.assertEqual(user["billing_state"], "revoked")
        self.assertEqual(self.database.effective_entitlement(user)["effective_plan"], "free")

    def test_unknown_product_updated_uses_existing_paid_plan(self):
        self.database.sync_polar_subscription_webhook(
            "subscription.active",
            {
                "customer": {"id": "cus_5", "email": "carry@example.com"},
                "status": "active",
                "product": {"id": "prod_pro"},
            },
            "pro",
        )

        payload = {
            "type": "subscription.updated",
            "data": {
                "customer": {"id": "cus_5", "email": "carry@example.com"},
                "status": "past_due",
                "current_period_end": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "product": {"id": "unknown_product"},
            },
        }
        body = json.dumps(payload).encode("utf-8")
        headers = _signed_headers(self.signing_key, body, webhook_id="evt_unknown_updated")
        resp = self.client.post("/webhooks/polar", data=body, headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("status"), "ok")

        user = self.database.get_user_by_email("carry@example.com")
        self.assertEqual(user["plan"], "pro")
        self.assertEqual(user["billing_state"], "past_due")

    def test_webhook_claim_released_when_processing_throws(self):
        original_sync = self.app_module.sync_polar_subscription_webhook

        def _boom(*args, **kwargs):
            raise RuntimeError("boom")

        self.app_module.sync_polar_subscription_webhook = _boom
        try:
            payload = {
                "type": "subscription.active",
                "data": {
                    "customer": {"id": "cus_6", "email": "boom@example.com"},
                    "product": {"id": "prod_pro"},
                    "status": "active",
                },
            }
            body = json.dumps(payload).encode("utf-8")
            headers = _signed_headers(self.signing_key, body, webhook_id="evt_release")

            first = self.client.post("/webhooks/polar", data=body, headers=headers)
            self.assertEqual(first.status_code, 500)

            second = self.client.post("/webhooks/polar", data=body, headers=headers)
            self.assertEqual(second.status_code, 500)
            self.assertNotEqual(second.get_json().get("message"), "duplicate")
        finally:
            self.app_module.sync_polar_subscription_webhook = original_sync


if __name__ == "__main__":
    unittest.main()
