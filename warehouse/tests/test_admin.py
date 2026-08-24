from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from warehouse.models import Order, Product, ShippingBox


class AdminInterfaceTests(TestCase):
    """Test custom warehouse admin site branding and registration."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin_test@example.com",
            password="testpassword123"
        )
        self.client.force_login(self.admin_user)

    def test_admin_site_custom_titles(self):
        """Verify custom admin branding headers and titles."""
        self.assertEqual(admin.site.site_header, "Warehouse Box Selection Operations")
        self.assertEqual(admin.site.site_title, "Warehouse Admin Portal")
        self.assertEqual(admin.site.index_title, "Fulfillment & Catalog Management")

    def test_admin_index_renders_custom_theme(self):
        """GET /admin/ renders custom theme branding."""
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warehouse Fulfillment")
        self.assertContains(response, "Admin Portal")
        self.assertContains(response, "admin_custom.css")

    def test_admin_models_registered(self):
        """Verify Product, ShippingBox, and Order are registered in admin."""
        self.assertIn(Product, admin.site._registry)
        self.assertIn(ShippingBox, admin.site._registry)
        self.assertIn(Order, admin.site._registry)
