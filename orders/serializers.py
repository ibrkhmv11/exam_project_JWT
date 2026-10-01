from django.db import transaction
from rest_framework import serializers

from carts.models import Cart
from products.models import Product

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_that_time",
            "subtotal",
        )

    def get_subtotal(self, obj):
        return (
            obj.price_at_that_time
            * obj.quantity
        )

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "username",
            "total_price",
            "status",
            "shipping_address",
            "items",
            "created_at",
        )

        read_only_fields = (
            "id",
            "username",
            "total_price",
            "status",
            "created_at",
        )

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(
        min_length=5
    )

    def validate_shipping_address(self, value):
        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError(
                "Yetkazib berish manzili juda qisqa."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        try:
            cart = Cart.objects.prefetch_related(
                "items__product"
            ).get(
                user=user
            )

        except Cart.DoesNotExist:
            raise serializers.ValidationError(
                "Savat topilmadi."
            )

        cart_items = list(
            cart.items.all()
        )

        if not cart_items:
            raise serializers.ValidationError(
                "Savat bo'sh."
            )

        total_price = 0

        locked_products = {}

        for item in cart_items:
            product = Product.objects.select_for_update().get(
                pk=item.product_id
            )

            if product.stock < item.quantity:
                raise serializers.ValidationError({
                    "stock": (
                        f"{product.name} mahsulotidan "
                        f"omborda faqat {product.stock} ta mavjud."
                    )
                })

            locked_products[product.id] = product

            total_price += (
                product.price
                * item.quantity
            )

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            shipping_address=validated_data[
                "shipping_address"
            ]
        )

        for item in cart_items:
            product = locked_products[
                item.product_id
            ]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price_at_that_time=product.price
            )

            product.stock -= item.quantity

            product.save(
                update_fields=["stock"]
            )

        cart.items.all().delete()

        return order

class AdminOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "status",
        )

    def validate_status(self, value):
        allowed_statuses = [
            "pending",
            "shipping",
            "completed",
            "cancelled",
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Noto'g'ri order status."
            )

        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get(
            "status",
            instance.status
        )

        instance.save(
            update_fields=["status"]
        )

        return instance