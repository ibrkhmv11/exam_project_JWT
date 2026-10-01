from django.urls import path

from .views import (
    CategoryListCreateView,
    ProductListCreateView,
    ProductDetailView,
    LikeToggleView,
    LikeListView,
    ProductCommentView
)


urlpatterns = [
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category-list-create",
    ),

    path(
        "products/",
        ProductListCreateView.as_view(),
        name="product-list-create",
    ),

    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),

    path(
        "products/<int:pk>/like/",
        LikeToggleView.as_view(),
        name="product-like",
    ),

    path(
        "likes/",
        LikeListView.as_view(),
        name="like-list",
    ),
   path(
    "products/<int:pk>/comments/",
    ProductCommentView.as_view(),
    name="product-comments"
   ),
]