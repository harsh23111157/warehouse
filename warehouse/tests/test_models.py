from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from warehouse.models import Product, ShippingBox, Order, OrderItem


class ProductModelTests(TestCase):
    """Test suite for Product domain model invariants and properties."""

    def setUp(self):
        self.product = Product.objects.create(
            sku="SKU-MUG-001",
            name="Ceramic Coffee Mug",
            length=Decimal("12.50"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.450")
        )

    def test_product_creation_and_volume(self):
        """Verify volume is correctly calculated as L * W * H."""
        self.assertEqual(self.product.sku, "SKU-MUG-001")
        expected_volume = Decimal("12.50") * Decimal("10.00") * Decimal("10.00")
        self.assertEqual(self.product.volume, expected_volume)
        self.assertEqual(
            self.product.dimensions_tuple,
            (Decimal("12.50"), Decimal("10.00"), Decimal("10.00"))
        )

    def test_product_clean_valid(self):
        """Valid product clean() passes without error."""
        self.product.full_clean()

    def test_product_rejects_non_positive_length(self):
        """Product length <= 0 must fail validation."""
        p_zero = Product(
            sku="SKU-BAD-1",
            name="Bad Item",
            length=Decimal("0.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        with self.assertRaises(ValidationError):
            p_zero.full_clean()

        p_neg = Product(
            sku="SKU-BAD-2",
            name="Bad Item Negative",
            length=Decimal("-5.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.000")
        )
        with self.assertRaises(ValidationError):
            p_neg.full_clean()

    def test_product_rejects_non_positive_weight(self):
        """Product weight <= 0 must fail validation."""
        p_zero_weight = Product(
            sku="SKU-WEIGHT-0",
            name="Zero Weight",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.000")
        )
        with self.assertRaises(ValidationError):
            p_zero_weight.full_clean()


class ShippingBoxModelTests(TestCase):
    """Test suite for ShippingBox domain model invariants and properties."""

    def setUp(self):
        self.box = ShippingBox.objects.create(
            name="Box 1 - Small Mailer",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50")
        )

    def test_shipping_box_volume_and_dimensions(self):
        """Verify usable volume is calculated correctly."""
        expected_volume = Decimal("20.00") * Decimal("15.00") * Decimal("10.00")
        self.assertEqual(self.box.volume, expected_volume)
        self.assertEqual(
            self.box.dimensions_tuple,
            (Decimal("20.00"), Decimal("15.00"), Decimal("10.00"))
        )

    def test_shipping_box_rejects_negative_cost(self):
        """Box cost < 0 must fail validation."""
        bad_box = ShippingBox(
            name="Bad Box Negative Cost",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("-0.50")
        )
        with self.assertRaises(ValidationError):
            bad_box.full_clean()

    def test_shipping_box_rejects_zero_dimension(self):
        """Box with zero dimension must fail validation."""
        bad_box = ShippingBox(
            name="Zero Height Box",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("0.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.00")
        )
        with self.assertRaises(ValidationError):
            bad_box.full_clean()


class OrderModelTests(TestCase):
    """Test suite for Order and OrderItem relationships and aggregations."""

    def setUp(self):
        self.p1 = Product.objects.create(
            sku="SKU-BOOK",
            name="Hardcover Book",
            length=Decimal("22.00"),
            width=Decimal("15.00"),
            height=Decimal("3.50"),
            weight=Decimal("0.800")
        )
        self.p2 = Product.objects.create(
            sku="SKU-PEN",
            name="Gel Pen Pack",
            length=Decimal("15.00"),
            width=Decimal("5.00"),
            height=Decimal("2.00"),
            weight=Decimal("0.100")
        )
        self.order = Order.objects.create(notes="Urgent shipment")

    def test_order_total_weight_calculation(self):
        """Total order weight must equal sum(product_weight * quantity)."""
        OrderItem.objects.create(order=self.order, product=self.p1, quantity=2)  # 2 * 0.800 = 1.600
        OrderItem.objects.create(order=self.order, product=self.p2, quantity=3)  # 3 * 0.100 = 0.300

        self.assertEqual(self.order.total_weight, Decimal("1.900"))
        self.assertEqual(self.order.total_item_count, 5)

    def test_order_item_rejects_zero_quantity(self):
        """OrderItem quantity < 1 must fail validation."""
        item = OrderItem(order=self.order, product=self.p1, quantity=0)
        with self.assertRaises(ValidationError):
            item.full_clean()
