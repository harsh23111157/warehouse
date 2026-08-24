from decimal import Decimal
from unittest.mock import patch
from django.test import Client, TestCase
from django.urls import reverse
from warehouse.models import Order, OrderItem, Product, ShippingBox


class WarehouseViewTests(TestCase):
    """
    Integration tests for order creation, recommendation rendering, and catalog views.
    """

    def setUp(self):
        self.client = Client()
        self.ai_patcher = patch(
            "warehouse.views.generate_ai_explanation",
            return_value={"available": False, "explanation": None, "status": "MOCKED"}
        )
        self.ai_patcher.start()

        # Create test products
        self.product_mug = Product.objects.create(
            sku="SKU-MUG-1",
            name="Coffee Mug",
            length=Decimal("12.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.400")
        )
        self.product_oversized = Product.objects.create(
            sku="SKU-OVERSIZED",
            name="Huge Generator",
            length=Decimal("150.00"),
            width=Decimal("100.00"),
            height=Decimal("80.00"),
            weight=Decimal("60.000")
        )

        # Create test boxes
        self.box_small = ShippingBox.objects.create(
            name="Small Mailer Box",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("12.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50")
        )
        self.box_large = ShippingBox.objects.create(
            name="Large Carton",
            length=Decimal("40.00"),
            width=Decimal("30.00"),
            height=Decimal("25.00"),
            max_weight=Decimal("15.000"),
            cost=Decimal("3.50")
        )

    def tearDown(self):
        self.ai_patcher.stop()

    def test_order_create_view_get(self):
        """GET / returns 200 and renders order creation form."""
        response = self.client.get(reverse("warehouse:order_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Order &amp; Select Box")
        self.assertContains(response, "Coffee Mug")

    def test_order_create_view_post_valid_redirects(self):
        """POST / with valid items creates order and redirects to recommendation view."""
        post_data = {
            "notes": "Test Order #100",
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": str(self.product_mug.id),
            "items-0-quantity": "2",
        }
        response = self.client.post(reverse("warehouse:order_create"), post_data)
        self.assertEqual(response.status_code, 302)

        # Verify order in DB
        order = Order.objects.latest("id")
        self.assertEqual(order.notes, "Test Order #100")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertRedirects(response, reverse("warehouse:order_recommendation", kwargs={"order_id": order.id}))

    def test_order_create_view_post_invalid_re_renders_errors(self):
        """POST / with empty items re-renders 200 with validation error."""
        post_data = {
            "notes": "Empty Order",
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": "",
            "items-0-quantity": "1",
        }
        response = self.client.post(reverse("warehouse:order_create"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The order must contain at least one valid product.")
        self.assertEqual(Order.objects.count(), 0)

    def test_recommendation_view_renders_winner_and_explanation(self):
        """GET recommendation view renders recommended box card and explanation."""
        order = Order.objects.create(notes="Fulfillment Order")
        OrderItem.objects.create(order=order, product=self.product_mug, quantity=1)

        url = reverse("warehouse:order_recommendation", kwargs={"order_id": order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommended Box")
        self.assertContains(response, "Small Mailer Box")
        self.assertContains(response, "Candidate Boxes Evaluation")

    def test_recommendation_view_renders_no_fit_state(self):
        """GET recommendation view with oversized item renders 'No Available Box' banner."""
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_oversized, quantity=1)

        url = reverse("warehouse:order_recommendation", kwargs={"order_id": order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Available Box Can Ship This Order")
        self.assertContains(response, "Disqualified")

    def test_recommendation_view_404_for_nonexistent_order(self):
        """GET recommendation for nonexistent order returns 404."""
        url = reverse("warehouse:order_recommendation", kwargs={"order_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_product_list_view(self):
        """GET /products/ returns 200 and lists products."""
        response = self.client.get(reverse("warehouse:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warehouse Product Catalog")
        self.assertContains(response, "SKU-MUG-1")

    def test_box_list_view(self):
        """GET /boxes/ returns 200 and lists boxes."""
        response = self.client.get(reverse("warehouse:box_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shipping Box Inventory")
        self.assertContains(response, "Small Mailer Box")

    def test_order_ai_explanation_json_endpoint(self):
        """GET /order/<id>/ai-explanation/ returns JSON without blocking."""
        order = Order.objects.create(notes="Async AI Test")
        OrderItem.objects.create(order=order, product=self.product_mug, quantity=1)

        url = reverse("warehouse:order_ai_explanation", kwargs={"order_id": order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        json_data = response.json()
        self.assertIn("available", json_data)
        self.assertIn("status", json_data)

