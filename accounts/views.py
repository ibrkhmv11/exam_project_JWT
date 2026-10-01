from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "message": drf_serializers.CharField(),
                    "user": ProfileSerializer(),
                },
            )
        },
        description="Yangi foydalanuvchini ro'yxatdan o'tkazadi.",
    )
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            {
                "message": (
                    "Muvaffaqiyatli "
                    "ro'yxatdan o'tdingiz."
                ),
                "user": ProfileSerializer(
                    user
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "message": drf_serializers.CharField(),
                    "token": drf_serializers.CharField(),
                    "user": ProfileSerializer(),
                },
            )
        },
        description="Login qiladi va Token qaytaradi.",
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        token = serializer.validated_data[
            "token"
        ]

        return Response(
            {
                "message": (
                    "Muvaffaqiyatli login qilindi."
                ),
                "token": token.key,
                "user": ProfileSerializer(
                    user
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        responses={
            200: ProfileSerializer
        },
        description=(
            "Joriy login qilgan "
            "foydalanuvchi profilini chiqaradi."
        ),
    )
    def get(self, request):
        serializer = ProfileSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )