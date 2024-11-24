from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        description="Obtain a pair of JWT tokens (access and refresh)",
        request=CustomTokenObtainPairSerializer,
        responses={200: {"description": "JWT Tokens", "content": {"application/json": {"example": {"access": "your-access-token", "refresh": "your-refresh-token"}}}},
        400: {"description": "Validation Error", "content": {"application/json": {"example": {"detail": "Invalid credentials"}}}}},
        parameters=[
            OpenApiParameter(
                name="username",
                type=OpenApiTypes.STR,
                location="form",
                description="Username of the user"
            ),
            OpenApiParameter(
                name="password",
                type=OpenApiTypes.STR,
                location="form",
                description="Password of the user"
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description="Register a new user",
        request=UserSerializer,
        responses={201: UserSerializer,  
            400: {
                "description": "Validation Error", 
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Username already exists" 
                        }
                    }
                }
            }},
        parameters=[
            OpenApiParameter(
                name="email",
                type=OpenApiTypes.STR,
                location="form",
                description="Email of the new user"
            ),
            OpenApiParameter(
                name="username",
                type=OpenApiTypes.STR,
                location="form",
                description="Username of the new user"
            ),
            OpenApiParameter(
                name="password",
                type=OpenApiTypes.STR,
                location="form",
                description="Password for the new user"
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)