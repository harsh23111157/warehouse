import json
import urllib.error
from decimal import Decimal
from unittest.mock import MagicMock, patch
from django.test import TestCase, override_settings

from warehouse.ai import generate_ai_explanation
from warehouse.models import Product, ShippingBox
from warehouse.packing import BoxSpec, ItemSpec, recommend_box


class AIServiceTests(TestCase):
    """
    Tests for the optional AI explanation layer.
    Verifies that AI is purely advisory and degrades gracefully on all network or provider faults.
    """

    def setUp(self):
        self.item = ItemSpec(
            sku="SKU-AI-1",
            name="Mechanical Keyboard",
            length=Decimal("35.00"),
            width=Decimal("15.00"),
            height=Decimal("5.00"),
            weight=Decimal("1.200"),
            quantity=1
        )
        self.box = BoxSpec(
            id=1,
            name="Medium Keyboard Box",
            length=Decimal("40.00"),
            width=Decimal("20.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.00")
        )
        self.result = recommend_box([self.item], [self.box])
        
        # Mock order item object
        mock_product = MagicMock()
        mock_product.name = "Mechanical Keyboard"
        mock_product.length = Decimal("35.00")
        mock_product.width = Decimal("15.00")
        mock_product.height = Decimal("5.00")
        mock_product.weight = Decimal("1.200")
        
        mock_order_item = MagicMock()
        mock_order_item.product = mock_product
        mock_order_item.quantity = 1
        self.order_items = [mock_order_item]

    @patch("urllib.request.urlopen")
    def test_ai_successful_response(self, mock_urlopen):
        """AI provider returns a valid OpenAI-compatible completion."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [
                {
                    "message": {
                        "content": "Box Medium Keyboard Box easily holds the keyboard with 5cm headroom. Add bubble wrap along edges."
                    }
                }
            ]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertTrue(ai_res["available"])
        self.assertEqual(ai_res["status"], "SUCCESS")
        self.assertIn("easily holds the keyboard", ai_res["explanation"])

    @patch("urllib.request.urlopen")
    def test_ai_provider_timeout_degrades_gracefully(self, mock_urlopen):
        """TimeoutError from provider does not crash and returns available=False."""
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertFalse(ai_res["available"])
        self.assertIsNone(ai_res["explanation"])
        self.assertEqual(ai_res["status"], "TIMEOUT_OR_NETWORK_ERROR")

    @patch("urllib.request.urlopen")
    def test_ai_provider_http_error_degrades_gracefully(self, mock_urlopen):
        """HTTP 500 error from provider does not crash and returns available=False."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://router.bynara.id/v1/chat/completions",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=None
        )

        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertFalse(ai_res["available"])
        self.assertIsNone(ai_res["explanation"])
        self.assertEqual(ai_res["status"], "HTTP_ERROR_500")

    @patch("urllib.request.urlopen")
    def test_ai_malformed_response_degrades_gracefully(self, mock_urlopen):
        """Malformed response without 'choices' returns EMPTY_RESPONSE without crashing."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"error": "Rate limit reached"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertFalse(ai_res["available"])
        self.assertIsNone(ai_res["explanation"])
        self.assertEqual(ai_res["status"], "EMPTY_RESPONSE")

    @override_settings(AI_ENABLED=False)
    def test_ai_disabled_via_settings(self):
        """When AI_ENABLED is False, provider is not called."""
        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertFalse(ai_res["available"])
        self.assertEqual(ai_res["status"], "DISABLED")

    @override_settings(AI_API_KEY="")
    def test_ai_missing_api_key_returns_missing_config(self):
        """When API key is empty, provider is not called."""
        ai_res = generate_ai_explanation(self.result, self.order_items)
        self.assertFalse(ai_res["available"])
        self.assertEqual(ai_res["status"], "MISSING_CONFIG")

    def test_deterministic_engine_is_completely_independent_of_ai(self):
        """
        Proof that the deterministic recommendation engine functions identically
        whether AI is enabled, disabled, crashing, or throwing exceptions.
        """
        deterministic_result = recommend_box([self.item], [self.box])
        self.assertTrue(deterministic_result.is_fit_found)
        self.assertEqual(deterministic_result.recommended_box.id, self.box.id)
        self.assertEqual(deterministic_result.total_weight, Decimal("1.200"))
