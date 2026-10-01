from django.shortcuts import get_object_or_404

from django_filters.rest_framework import (
    DjangoFilterBackend,
)
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ProductFilter
from .models import (
    Category,
    Comment,
    Like,
    Product,
)
from .pagination import ProductPagination
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    LikeSerializer,
    LikeToggleSerializer,
    ProductSerializer,
)


class CategoryListCreateView(APIView):
    permission_classes = [
        IsAdminOrReadOnly
    ]

    @extend_schema(
        tags=["Categories"],
        responses={
            200: CategorySerializer(
                many=True
            )
        },
        description=(
            "Barcha kategoriyalar "
            "ro'yxatini chiqaradi."
        ),
    )
    def get(self, request):
        categories = Category.objects.all()

        serializer = CategorySerializer(
            categories,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Categories"],
        request=CategorySerializer,
        responses={
            201: CategorySerializer
        },
        description=(
            "Yangi kategoriya yaratadi. "
            "Faqat admin."
        ),
    )
    def post(self, request):
        serializer = CategorySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProductListCreateView(APIView):
    permission_classes = [
        IsAdminOrReadOnly
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
    ]

    ordering = [
        "-created_at"
    ]

    @extend_schema(
        tags=["Products"],
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Sahifa raqami.",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description=(
                    "Bir sahifadagi "
                    "mahsulotlar soni."
                ),
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description=(
                    "Name va description "
                    "bo'yicha qidirish."
                ),
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                description=(
                    "Category slug "
                    "bo'yicha filter."
                ),
            ),
            OpenApiParameter(
                name="min_price",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Minimal narx.",
            ),
            OpenApiParameter(
                name="max_price",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Maksimal narx.",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description=(
                    "Masalan: price, "
                    "-price, -created_at"
                ),
            ),
        ],
        responses={
            200: ProductSerializer(
                many=True
            )
        },
        description=(
            "Mahsulotlar ro'yxati. "
            "Pagination, Filter, "
            "Search va Ordering mavjud."
        ),
    )
    def get(self, request):
        queryset = (
            Product.objects
            .select_related("category")
            .all()
        )

        for backend in self.filter_backends:
            queryset = (
                backend()
                .filter_queryset(
                    request,
                    queryset,
                    self
                )
            )

        paginator = ProductPagination()

        page = paginator.paginate_queryset(
            queryset,
            request
        )

        serializer = ProductSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    @extend_schema(
        tags=["Products"],
        request=ProductSerializer,
        responses={
            201: ProductSerializer
        },
        description=(
            "Yangi mahsulot yaratadi. "
            "Faqat admin."
        ),
    )
    def post(self, request):
        serializer = ProductSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    permission_classes = [
        IsAdminOrReadOnly
    ]

    def get_object(self, pk):
        return get_object_or_404(
            Product.objects.select_related(
                "category"
            ),
            pk=pk
        )

    @extend_schema(
        tags=["Products"],
        responses={
            200: ProductSerializer
        },
        description=(
            "Bitta mahsulotni chiqaradi."
        ),
    )
    def get(self, request, pk):
        product = self.get_object(pk)

        serializer = ProductSerializer(
            product
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Products"],
        request=ProductSerializer,
        responses={
            200: ProductSerializer
        },
        description=(
            "Mahsulotni to'liq "
            "yangilaydi. Faqat admin."
        ),
    )
    def put(self, request, pk):
        product = self.get_object(pk)

        serializer = ProductSerializer(
            product,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Products"],
        request=ProductSerializer,
        responses={
            200: ProductSerializer
        },
        description=(
            "Mahsulotni qisman "
            "yangilaydi. Faqat admin."
        ),
    )
    def patch(self, request, pk):
        product = self.get_object(pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Products"],
        responses={
            204: OpenApiResponse(
                description=(
                    "Mahsulot o'chirildi."
                )
            )
        },
        description=(
            "Mahsulotni o'chiradi. "
            "Faqat admin."
        ),
    )
    def delete(self, request, pk):
        product = self.get_object(pk)

        product.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class LikeToggleView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Likes"],
        request=None,
        responses={
            200: inline_serializer(
                name="LikeToggleResponse",
                fields={
                    "liked": (
                        drf_serializers
                        .BooleanField()
                    ),
                    "message": (
                        drf_serializers
                        .CharField()
                    ),
                    "product_id": (
                        drf_serializers
                        .IntegerField()
                    ),
                },
            )
        },
        description=(
            "Mahsulotni like/unlike qiladi."
        ),
    )
    def post(self, request, pk):
        serializer = LikeToggleSerializer(
            data={
                "product_id": pk
            },
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = serializer.save()

        return Response(
            result,
            status=status.HTTP_200_OK
        )


class LikeListView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Likes"],
        responses={
            200: LikeSerializer(
                many=True
            )
        },
        description=(
            "Joriy userning barcha "
            "like qilgan mahsulotlari."
        ),
    )
    def get(self, request):
        likes = (
            Like.objects
            .filter(
                user=request.user
            )
            .select_related(
                "product",
                "product__category",
            )
        )

        serializer = LikeSerializer(
            likes,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductCommentView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated()
            ]

        return [
            AllowAny()
        ]

    def get_product(self, pk):
        return get_object_or_404(
            Product,
            pk=pk
        )

    @extend_schema(
        tags=["Comments"],
        responses={
            200: CommentSerializer(
                many=True
            )
        },
        description=(
            "Mahsulotga yozilgan "
            "barcha commentlarni chiqaradi."
        ),
    )
    def get(self, request, pk):
        product = self.get_product(pk)

        comments = (
            Comment.objects
            .filter(
                product=product
            )
            .select_related(
                "user",
                "product",
            )
            .order_by(
                "-created_at"
            )
        )

        serializer = CommentSerializer(
            comments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Comments"],
        request=CommentSerializer,
        responses={
            201: CommentSerializer
        },
        description=(
            "Mahsulotga comment va "
            "rating yozadi."
        ),
    )
    def post(self, request, pk):
        product = self.get_product(pk)

        serializer = CommentSerializer(
            data=request.data,
            context={
                "request": request,
                "product": product,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )