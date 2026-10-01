from django.utils.text import slugify
from rest_framework import serializers

from .models import (
    Category,
    Product,
    Like,
    Comment,
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
        )

        read_only_fields = (
            "id",
            "slug",
        )

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Kategoriya nomi juda qisqa."
            )

        return value

    def create(self, validated_data):
        name = validated_data["name"]

        validated_data["slug"] = slugify(name)

        return Category.objects.create(
            **validated_data
        )

    def update(self, instance, validated_data):
        name = validated_data.get(
            "name",
            instance.name
        )

        validated_data["slug"] = slugify(name)

        return super().update(
            instance,
            validated_data
        )


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "image",
            "created_at",
        )

        read_only_fields = (
            "id",
            "slug",
            "created_at",
            "category_name",
        )

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Mahsulot nomi juda qisqa."
            )

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Mahsulot narxi 0 dan katta bo'lishi kerak."
            )

        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock manfiy bo'lishi mumkin emas."
            )

        return value

    def create(self, validated_data):
        name = validated_data["name"]

        validated_data["slug"] = slugify(name)

        return Product.objects.create(
            **validated_data
        )

    def update(self, instance, validated_data):
        name = validated_data.get(
            "name",
            instance.name
        )

        validated_data["slug"] = slugify(name)

        return super().update(
            instance,
            validated_data
        )


class LikeToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(
        write_only=True
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

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product_id"]

        like, created = Like.objects.get_or_create(
            user=user,
            product=product
        )

        if created:
            return {
                "liked": True,
                "message": "Mahsulot sevimlilarga qo'shildi.",
                "product_id": product.id,
            }

        like.delete()

        return {
            "liked": False,
            "message": "Mahsulot sevimlilardan olib tashlandi.",
            "product_id": product.id,
        }


class LikeSerializer(serializers.ModelSerializer):
    product = ProductSerializer(
        read_only=True
    )

    class Meta:
        model = Like
        fields = (
            "id",
            "product",
            "created_at",
        )

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "username",
            "product",
            "text",
            "rating",
            "created_at",
        )

        read_only_fields = (
            "id",
            "user",
            "username",
            "product",
            "created_at",
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating 1 dan 5 gacha bo'lishi kerak."
            )

        return value

    def validate_text(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Sharh juda qisqa."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]
        product = self.context["product"]

        return Comment.objects.create(
            user=request.user,
            product=product,
            **validated_data
        )