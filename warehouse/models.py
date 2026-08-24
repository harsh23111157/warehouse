from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """
    Physical merchandise item stored and shipped from the ecommerce warehouse.
    Dimensions are in centimeters (cm); weight is in kilograms (kg).
    """
    sku = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="SKU",
        help_text="Unique Stock Keeping Unit identifier."
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Product Name"
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Length (cm)",
        help_text="Rigid bounding length in centimeters."
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Width (cm)",
        help_text="Rigid bounding width in centimeters."
    )
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Height (cm)",
        help_text="Rigid bounding height in centimeters."
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Weight (kg)",
        help_text="Product unit weight in kilograms."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this product is available for order fulfillment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        ordering = ["name", "sku"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return f"{self.name} ({self.sku}) - {self.length}x{self.width}x{self.height}cm, {self.weight}kg"

    @property
    def volume(self) -> Decimal:
        """Calculates internal bounding volume in cm³."""
        return self.length * self.width * self.height

    @property
    def dimensions_tuple(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns ordered dimension tuple (L, W, H)."""
        return (self.length, self.width, self.height)

    def clean(self):
        super().clean()
        if self.length is not None and self.length <= Decimal("0.00"):
            raise ValidationError({"length": "Product length must be strictly greater than zero."})
        if self.width is not None and self.width <= Decimal("0.00"):
            raise ValidationError({"width": "Product width must be strictly greater than zero."})
        if self.height is not None and self.height <= Decimal("0.00"):
            raise ValidationError({"height": "Product height must be strictly greater than zero."})
        if self.weight is not None and self.weight <= Decimal("0.000"):
            raise ValidationError({"weight": "Product weight must be strictly greater than zero."})


class ShippingBox(models.Model):
    """
    Standard packaging box available in warehouse inventory.
    Dimensions represent internal usable space in centimeters (cm);
    max_weight represents payload limit in kilograms (kg); cost is in currency units ($).
    """
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Box Name",
        help_text="Unique identifier or descriptive name (e.g. 'Box 1 - Small Mailer')."
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Internal Length (cm)",
        help_text="Internal usable length in centimeters."
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Internal Width (cm)",
        help_text="Internal usable width in centimeters."
    )
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Internal Height (cm)",
        help_text="Internal usable height in centimeters."
    )
    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Max Weight Capacity (kg)",
        help_text="Maximum payload weight the box can physically support."
    )
    cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Unit Cost ($)",
        help_text="Cost per box unit in dollars."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this box is currently available for packaging recommendations."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        ordering = ["cost", "name"]
        verbose_name = "Shipping Box"
        verbose_name_plural = "Shipping Boxes"

    def __str__(self) -> str:
        return f"{self.name} ({self.length}x{self.width}x{self.height}cm, max {self.max_weight}kg, ${self.cost})"

    @property
    def volume(self) -> Decimal:
        """Calculates usable internal volume in cm³."""
        return self.length * self.width * self.height

    @property
    def dimensions_tuple(self) -> tuple[Decimal, Decimal, Decimal]:
        """Returns ordered internal dimension tuple (L, W, H)."""
        return (self.length, self.width, self.height)

    def clean(self):
        super().clean()
        if self.length is not None and self.length <= Decimal("0.00"):
            raise ValidationError({"length": "Box internal length must be strictly greater than zero."})
        if self.width is not None and self.width <= Decimal("0.00"):
            raise ValidationError({"width": "Box internal width must be strictly greater than zero."})
        if self.height is not None and self.height <= Decimal("0.00"):
            raise ValidationError({"height": "Box internal height must be strictly greater than zero."})
        if self.max_weight is not None and self.max_weight <= Decimal("0.000"):
            raise ValidationError({"max_weight": "Box maximum weight capacity must be strictly greater than zero."})
        if self.cost is not None and self.cost < Decimal("0.00"):
            raise ValidationError({"cost": "Box unit cost cannot be negative."})


class Order(models.Model):
    """
    Warehouse fulfillment order placed for packing recommendation.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Staff Notes",
        help_text="Optional reference or packing instructions."
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"Order #{self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def total_weight(self) -> Decimal:
        """Calculates aggregate weight of all order items in kg."""
        total = Decimal("0.000")
        for item in self.items.all():
            if item.product and item.product.weight and item.quantity:
                total += item.product.weight * Decimal(item.quantity)
        return total

    @property
    def total_item_count(self) -> int:
        """Returns total unit count of all line items."""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Line item association between an Order and a Product.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantity"
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name} (Order #{self.order_id})"

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({"quantity": "Quantity must be at least 1."})
