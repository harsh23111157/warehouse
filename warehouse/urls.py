from django.urls import path
from warehouse.views import (
    BoxListView,
    OrderAIExplanationView,
    OrderCreateView,
    OrderRecommendationView,
    ProductListView,
)

app_name = "warehouse"

urlpatterns = [
    path("", OrderCreateView.as_view(), name="order_create"),
    path("order/<int:order_id>/recommendation/", OrderRecommendationView.as_view(), name="order_recommendation"),
    path("order/<int:order_id>/ai-explanation/", OrderAIExplanationView.as_view(), name="order_ai_explanation"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("boxes/", BoxListView.as_view(), name="box_list"),
]
