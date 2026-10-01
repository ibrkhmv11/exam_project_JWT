from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "password",
            "confirm_password",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Parollar bir xil emas."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            role="customer",
            **validated_data
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Username yoki password noto'g'ri."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Foydalanuvchi faol emas."
            )

        token, created = Token.objects.get_or_create(
            user=user
        )

        attrs["user"] = user
        attrs["token"] = token

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "phone",
            "role",
            "first_name",
            "last_name",
        )

        read_only_fields = (
            "id",
            "username",
            "role",
        )