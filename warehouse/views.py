from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View

from warehouse.ai import generate_ai_explanation
from warehouse.forms import OrderForm, OrderItemFormSet
from warehouse.models import Order, Product, ShippingBox
from warehouse.packing import BoxSpec, ItemSpec, recommend_box


class OrderCreateView(View):
    """
    Primary warehouse order creation workflow.
    GET: Render order header and dynamic product line items formset.
    POST: Validate inputs, persist Order + OrderItems, redirect to recommendation.
    """
    template_name = "warehouse/order_form.html"

    def get(self, request, *args, **kwargs):
        order = Order()
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order, prefix="items")
        products = Product.objects.filter(is_active=True).order_by("name")
        boxes_count = ShippingBox.objects.filter(is_active=True).count()

        context = {
            "form": form,
            "formset": formset,
            "products": products,
            "boxes_count": boxes_count,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        order = Order()
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order, prefix="items")

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                saved_order = form.save()
                formset.instance = saved_order
                formset.save()
            return redirect("warehouse:order_recommendation", order_id=saved_order.id)

        products = Product.objects.filter(is_active=True).order_by("name")
        boxes_count = ShippingBox.objects.filter(is_active=True).count()

        context = {
            "form": form,
            "formset": formset,
            "products": products,
            "boxes_count": boxes_count,
        }
        return render(request, self.template_name, context)


class OrderRecommendationView(View):
    """
    Computes and displays the deterministic box recommendation and full evaluation diagnostics instantly.
    The AI explanation is loaded asynchronously in the background so page load is < 0.05s.
    """
    template_name = "warehouse/recommendation_result.html"

    def get(self, request, order_id: int, *args, **kwargs):
        order = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            id=order_id
        )

        order_items = list(order.items.select_related("product").all())
        item_specs = [
            ItemSpec(
                sku=item.product.sku,
                name=item.product.name,
                length=item.product.length,
                width=item.product.width,
                height=item.product.height,
                weight=item.product.weight,
                quantity=item.quantity
            )
            for item in order_items
            if item.product
        ]

        active_boxes = ShippingBox.objects.filter(is_active=True).order_by("cost", "name")
        box_specs = [
            BoxSpec(
                id=b.id,
                name=b.name,
                length=b.length,
                width=b.width,
                height=b.height,
                max_weight=b.max_weight,
                cost=b.cost
            )
            for b in active_boxes
        ]

        # Instantaneous deterministic engine computation
        result = recommend_box(item_specs, box_specs) if item_specs else None

        context = {
            "order": order,
            "order_items": order_items,
            "result": result,
            "total_weight": result.total_weight if result else Decimal("0.000"),
            "total_items": result.total_items if result else 0,
        }
        return render(request, self.template_name, context)


class OrderAIExplanationView(View):
    """
    Asynchronous JSON endpoint for optional AI packing advice.
    Called via client-side fetch so main page load is instantaneous.
    """
    def get(self, request, order_id: int, *args, **kwargs):
        from django.http import JsonResponse
        order = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            id=order_id
        )

        order_items = list(order.items.select_related("product").all())
        item_specs = [
            ItemSpec(
                sku=item.product.sku,
                name=item.product.name,
                length=item.product.length,
                width=item.product.width,
                height=item.product.height,
                weight=item.product.weight,
                quantity=item.quantity
            )
            for item in order_items
            if item.product
        ]

        active_boxes = ShippingBox.objects.filter(is_active=True).order_by("cost", "name")
        box_specs = [
            BoxSpec(
                id=b.id,
                name=b.name,
                length=b.length,
                width=b.width,
                height=b.height,
                max_weight=b.max_weight,
                cost=b.cost
            )
            for b in active_boxes
        ]

        result = recommend_box(item_specs, box_specs) if item_specs else None
        ai_data = generate_ai_explanation(result, order_items) if result else {
            "available": False,
            "explanation": None,
            "status": "NO_DATA",
            "model": None,
            "tokens_used": 0
        }

        return JsonResponse(ai_data)



class ProductListView(ListView):
    """Warehouse product catalog view."""
    model = Product
    template_name = "warehouse/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by("name")


class BoxListView(ListView):
    """Warehouse shipping box catalog view."""
    model = ShippingBox
    template_name = "warehouse/box_list.html"
    context_object_name = "boxes"

    def get_queryset(self):
        return ShippingBox.objects.filter(is_active=True).order_by("cost", "name")
