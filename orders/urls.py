from django.urls import path

from .views import (
    AdminOrderListView,
    AdminOrderUpdateView,
    CheckoutView,
    OrderListView,
)


urlpatterns = [
    path(
        "orders/checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "orders/",
        OrderListView.as_view(),
        name="order-list",
    ),

    path(
        "admin/orders/",
        AdminOrderListView.as_view(),
        name="admin-order-list",
    ),

    path(
        "admin/orders/<int:pk>/",
        AdminOrderUpdateView.as_view(),
        name="admin-order-update",
    ),
]