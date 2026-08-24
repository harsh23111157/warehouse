from django.contrib import admin
from warehouse.models import Order, OrderItem, Product, ShippingBox


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "length", "width", "height", "weight", "volume_cm3", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "sku")
    ordering = ("name", "sku")

    @admin.display(description="Volume (cm³)")
    def volume_cm3(self, obj: Product) -> str:
        return f"{obj.volume:,.2f}"


@admin.register(ShippingBox)
class ShippingBoxAdmin(admin.ModelAdmin):
    list_display = ("name", "length", "width", "height", "max_weight", "cost", "volume_cm3", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("cost", "name")

    @admin.display(description="Usable Volume (cm³)")
    def volume_cm3(self, obj: ShippingBox) -> str:
        return f"{obj.volume:,.2f}"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ("product", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at", "total_items_display", "total_weight_display", "notes")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)

    @admin.display(description="Total Units")
    def total_items_display(self, obj: Order) -> int:
        return obj.total_item_count

    @admin.display(description="Total Weight (kg)")
    def total_weight_display(self, obj: Order) -> str:
        return f"{obj.total_weight:.3f} kg"


admin.site.site_header = "Warehouse Box Selection Operations"
admin.site.site_title = "Warehouse Admin Portal"
admin.site.index_title = "Fulfillment & Catalog Management"

