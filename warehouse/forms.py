from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from warehouse.models import Order, OrderItem, Product, ShippingBox


class OrderForm(forms.ModelForm):
    """
    Form for creating a new fulfillment order.
    """
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Optional reference (e.g. PO-9842, Fragile packing)",
            "maxlength": "255"
        }),
        label="Order Notes"
    )

    class Meta:
        model = Order
        fields = ["notes"]


class OrderItemForm(forms.ModelForm):
    """
    Line item form for product selection and quantity.
    """
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        empty_label="-- Select Product --",
        widget=forms.Select(attrs={"class": "form-control product-select"}),
        label="Product"
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control quantity-input",
            "min": "1",
            "step": "1"
        }),
        label="Quantity"
    )

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class BaseOrderItemFormSet(BaseInlineFormSet):
    """
    Validates that at least one valid product line item is submitted.
    """
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        valid_items_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                product = form.cleaned_data.get("product")
                quantity = form.cleaned_data.get("quantity")
                if product and quantity and quantity >= 1:
                    valid_items_count += 1

        if valid_items_count == 0:
            raise forms.ValidationError("The order must contain at least one valid product.")


OrderItemFormSet = inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    can_delete=True
)
