from decimal import Decimal
from django.test import TestCase
from warehouse.forms import OrderForm, OrderItemFormSet
from warehouse.models import Order, Product


class OrderFormTests(TestCase):
    """Test suite for Order and OrderItemFormSet validation rules."""

    def setUp(self):
        self.product = Product.objects.create(
            sku="SKU-FORM-1",
            name="Testing Widget",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )

    def test_order_form_valid(self):
        """OrderForm with optional note is valid."""
        form = OrderForm(data={"notes": "Priority Packaging"})
        self.assertTrue(form.is_valid())

    def test_order_item_formset_valid_single_item(self):
        """OrderItemFormSet with valid product and quantity is valid."""
        order = Order.objects.create()
        data = {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": str(self.product.id),
            "items-0-quantity": "2",
        }
        formset = OrderItemFormSet(data=data, instance=order, prefix="items")
        self.assertTrue(formset.is_valid())

    def test_order_item_formset_rejects_empty_items(self):
        """FormSet with no product selected fails validation."""
        order = Order.objects.create()
        data = {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": "",
            "items-0-quantity": "1",
        }
        formset = OrderItemFormSet(data=data, instance=order, prefix="items")
        self.assertFalse(formset.is_valid())
        self.assertIn("The order must contain at least one valid product.", formset.non_form_errors())

    def test_order_item_formset_rejects_zero_quantity(self):
        """FormSet with quantity 0 fails validation."""
        order = Order.objects.create()
        data = {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": str(self.product.id),
            "items-0-quantity": "0",
        }
        formset = OrderItemFormSet(data=data, instance=order, prefix="items")
        self.assertFalse(formset.is_valid())
