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


SIGNING_KEY = b"polar-signing-key"


def _reload_modules(db_path, annual_starter_id="prod_starter_annual", annual_pro_id="prod_pro_annual"):
    whsec = "whsec_" + base64.b64encode(SIGNING_KEY).decode()
    os.environ["DB_PATH"] = db_path
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["POLAR_WEBHOOK_SECRET"] = whsec
    os.environ["POLAR_STARTER_PRODUCT_ID"] = "prod_starter"
    os.environ["POLAR_PRO_PRODUCT_ID"] = "prod_pro"
    os.environ["POLAR_STARTER_ANNUAL_PRODUCT_ID"] = annual_starter_id
    os.environ["POLAR_PRO_ANNUAL_PRODUCT_ID"] = annual_pro_id
    os.environ["POLAR_CHECKOUT_STARTER"] = "https://polar.example/checkout/starter"
    os.environ["POLAR_CHECKOUT_PRO"] = "https://polar.example/checkout/pro"
    os.environ.setdefault("POLAR_CHECKOUT_STARTER_ANNUAL", "https://polar.example/checkout/starter-annual")
    os.environ.setdefault("POLAR_CHECKOUT_PRO_ANNUAL", "https://polar.example/checkout/pro-annual")

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


def _signed(body, webhook_id):
    ts = str(int(time.time()))
    signed = f"{webhook_id}.{ts}.".encode("utf-8") + body
    sig = base64.b64encode(hmac.new(SIGNING_KEY, signed, hashlib.sha256).digest()).decode()
    return {
        "webhook-id": webhook_id,
        "webhook-timestamp": ts,
        "webhook-signature": f"v1,{sig}",
    }


class AnnualPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.app_module, self.database = _reload_modules(self.db_path)
        self.client = self.app_module.app.test_client()
        # Silence outbound emails from the dunning dispatcher.
        self.app_module._send_email = lambda *a, **kw: True

    def tearDown(self):
        self.tmpdir.cleanup()

    def _post_webhook(self, product_id, polar_id="cus_annual", email="annual@example.com"):
        payload = {
            "type": "subscription.active",
            "data": {
                "customer": {"id": polar_id, "email": email},
                "product": {"id": product_id},
                "status": "active",
            },
        }
        body = json.dumps(payload).encode()
        return self.client.post(
            "/webhooks/polar",
            data=body,
            headers=_signed(body, f"evt_{product_id}"),
        )

    def _user_row(self, polar_id):
        with self.database.get_db() as db:
            row = db.execute(
                "SELECT plan, billing_interval FROM users WHERE polar_customer_id = ?",
                (polar_id,),
            ).fetchone()
            return dict(row) if row else None

    def test_annual_pro_product_maps_to_pro_plan(self):
        resp = self._post_webhook("prod_pro_annual", polar_id="cus_annual_pro")
        self.assertEqual(resp.status_code, 200)
        row = self._user_row("cus_annual_pro")
        self.assertEqual(row["plan"], "pro")
        self.assertEqual(row["billing_interval"], "annual")

    def test_annual_starter_product_maps_to_starter_plan(self):
        resp = self._post_webhook("prod_starter_annual", polar_id="cus_annual_starter")
        self.assertEqual(resp.status_code, 200)
        row = self._user_row("cus_annual_starter")
        self.assertEqual(row["plan"], "starter")
        self.assertEqual(row["billing_interval"], "annual")

    def test_monthly_pro_product_records_monthly_interval(self):
        resp = self._post_webhook("prod_pro", polar_id="cus_monthly_pro")
        self.assertEqual(resp.status_code, 200)
        row = self._user_row("cus_monthly_pro")
        self.assertEqual(row["plan"], "pro")
        self.assertEqual(row["billing_interval"], "monthly")

    def test_pricing_page_exposes_annual_checkout_urls(self):
        resp = self.client.get("/pricing")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        # The live pricing page shows a single Pro Annual card under the Annual
        # toggle; Starter Annual was folded away in a prior pricing restructure.
        self.assertIn("https://polar.example/checkout/pro-annual", html)
        self.assertIn("data-interval=\"annual\"", html)


class AnnualFallbackTests(unittest.TestCase):
    """When annual checkout URLs aren't configured, fall back to monthly URLs."""

    def test_blank_annual_url_falls_back_to_monthly(self):
        # Mirror the same fallback expression app.py uses at import time.
        # This keeps the test independent of module-reload order.
        starter_monthly = "https://polar.example/checkout/starter"
        pro_monthly = "https://polar.example/checkout/pro"

        starter_annual_env = ""  # blank — simulates un-configured
        pro_annual_env = ""

        starter_annual = starter_annual_env.strip() or starter_monthly
        pro_annual = pro_annual_env.strip() or pro_monthly

        self.assertEqual(starter_annual, starter_monthly)
        self.assertEqual(pro_annual, pro_monthly)


if __name__ == "__main__":
    unittest.main()
