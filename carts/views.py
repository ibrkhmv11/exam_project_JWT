from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart
from .serializers import (
    CartAddSerializer,
    CartItemSerializer,
    CartRemoveSerializer,
    CartSerializer,
)


class CartView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Cart"],
        responses={
            200: CartSerializer
        },
        description=(
            "Joriy userning savatini chiqaradi."
        ),
    )
    def get(self, request):
        cart, created = (
            Cart.objects
            .get_or_create(
                user=request.user
            )
        )

        cart = (
            Cart.objects
            .prefetch_related(
                "items__product__category"
            )
            .get(
                pk=cart.pk
            )
        )

        serializer = CartSerializer(
            cart
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CartAddView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Cart"],
        request=CartAddSerializer,
        responses={
            201: inline_serializer(
                name="CartAddResponse",
                fields={
                    "message": (
                        drf_serializers
                        .CharField()
                    ),
                    "item": (
                        CartItemSerializer()
                    ),
                },
            )
        },
        description=(
            "Mahsulotni savatga qo'shadi."
        ),
    )
    def post(self, request):
        serializer = CartAddSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        cart_item = serializer.save()

        return Response(
            {
                "message": (
                    "Mahsulot savatga qo'shildi."
                ),
                "item": CartItemSerializer(
                    cart_item
                ).data,
            },
            status=status.HTTP_201_CREATED
        )


class CartRemoveView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Cart"],
        request=CartRemoveSerializer,
        responses={
            200: inline_serializer(
                name="CartRemoveResponse",
                fields={
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
            "Mahsulotni savatdan o'chiradi."
        ),
    )
    def post(self, request):
        serializer = CartRemoveSerializer(
            data=request.data,
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