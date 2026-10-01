from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "quantity",
            "subtotal",
        )

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "items",
            "total_quantity",
            "total_price",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )

    def get_total_price(self, obj):
        total = 0

        for item in obj.items.all():
            total += (
                item.product.price
                * item.quantity
            )

        return total

    def get_total_quantity(self, obj):
        total = 0

        for item in obj.items.all():
            total += item.quantity

        return total

class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1
    )

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(
                id=value
            )

        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Mahsulot topilmadi."
            )

        return product

    def validate(self, attrs):
        product = attrs["product_id"]
        quantity = attrs["quantity"]

        if product.stock < quantity:
            raise serializers.ValidationError({
                "quantity": (
                    f"Omborda faqat {product.stock} ta mahsulot bor."
                )
            })

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        product = validated_data["product_id"]
        quantity = validated_data["quantity"]

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity
            }
        )

        if not created:
            new_quantity = (
                cart_item.quantity
                + quantity
            )

            if new_quantity > product.stock:
                raise serializers.ValidationError({
                    "quantity": (
                        f"Omborda faqat {product.stock} ta mahsulot bor."
                    )
                })

            cart_item.quantity = new_quantity
            cart_item.save()

        return cart_item

class CartRemoveSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(
                id=value
            )

        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Mahsulot topilmadi."
            )

        return product

    def create(self, validated_data):
        request = self.context["request"]
        product = validated_data["product_id"]

        try:
            cart = Cart.objects.get(
                user=request.user
            )

        except Cart.DoesNotExist:
            raise serializers.ValidationError(
                "Savat topilmadi."
            )

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product
            )

        except CartItem.DoesNotExist:
            raise serializers.ValidationError(
                "Bu mahsulot savatda mavjud emas."
            )

        cart_item.delete()

        return {
            "message": "Mahsulot savatdan o'chirildi.",
            "product_id": product.id,
        }