from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import (
    AdminOrderUpdateSerializer,
    CheckoutSerializer,
    OrderSerializer,
)


class CheckoutView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Orders"],
        request=CheckoutSerializer,
        responses={
            201: inline_serializer(
                name="CheckoutResponse",
                fields={
                    "message": (
                        drf_serializers
                        .CharField()
                    ),
                    "order": (
                        OrderSerializer()
                    ),
                },
            )
        },
        description=(
            "Savatdagi mahsulotlardan "
            "buyurtma yaratadi."
        ),
    )
    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = serializer.save()

        return Response(
            {
                "message": (
                    "Buyurtma muvaffaqiyatli "
                    "yaratildi."
                ),
                "order": OrderSerializer(
                    order
                ).data,
            },
            status=status.HTTP_201_CREATED
        )


class OrderListView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=["Orders"],
        responses={
            200: OrderSerializer(
                many=True
            )
        },
        description=(
            "Joriy userning barcha "
            "buyurtmalarini chiqaradi."
        ),
    )
    def get(self, request):
        orders = (
            Order.objects
            .filter(
                user=request.user
            )
            .prefetch_related(
                "items__product"
            )
            .order_by(
                "-created_at"
            )
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AdminOrderListView(APIView):
    permission_classes = [
        IsAdminUser
    ]

    @extend_schema(
        tags=["Admin Orders"],
        responses={
            200: OrderSerializer(
                many=True
            )
        },
        description=(
            "Barcha orderlarni chiqaradi. "
            "Faqat admin."
        ),
    )
    def get(self, request):
        orders = (
            Order.objects
            .select_related(
                "user"
            )
            .prefetch_related(
                "items__product"
            )
            .order_by(
                "-created_at"
            )
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AdminOrderUpdateView(APIView):
    permission_classes = [
        IsAdminUser
    ]

    @extend_schema(
        tags=["Admin Orders"],
        request=AdminOrderUpdateSerializer,
        responses={
            200: inline_serializer(
                name="AdminOrderUpdateResponse",
                fields={
                    "message": (
                        drf_serializers
                        .CharField()
                    ),
                    "order": (
                        OrderSerializer()
                    ),
                },
            )
        },
        description=(
            "Order statusini o'zgartiradi. "
            "Faqat admin."
        ),
    )
    def patch(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk
        )

        serializer = (
            AdminOrderUpdateSerializer(
                order,
                data=request.data,
                partial=True
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = serializer.save()

        return Response(
            {
                "message": (
                    "Order status yangilandi."
                ),
                "order": OrderSerializer(
                    order
                ).data,
            },
            status=status.HTTP_200_OK
        )