from django.urls import path

from .views import (
    CartAddView,
    CartRemoveView,
    CartView,
)


urlpatterns = [
    path(
        "cart/",
        CartView.as_view(),
        name="cart",
    ),

    path(
        "cart/add/",
        CartAddView.as_view(),
        name="cart-add",
    ),

    path(
        "cart/remove/",
        CartRemoveView.as_view(),
        name="cart-remove",
    ),
]