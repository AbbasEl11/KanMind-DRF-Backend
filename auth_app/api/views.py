"""
Authentication API views.

This module contains view classes for user registration and login endpoints.
"""

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    POST /api/registration/

    Allows unauthenticated users to create a new account. Upon successful
    registration, a token is generated and returned for immediate authentication.

    Permissions:
        - AllowAny: No authentication required

    Returns:
        201: Registration successful with token and user data
        400: Validation errors (password mismatch, email/username exists, etc.)
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def create(self, request):
        """
        Handle user registration request.

        Args:
            request: HTTP request containing registration data

        Returns:
            Response: User token and profile information
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        saved_account = serializer.save()

        token, created = Token.objects.get_or_create(user=saved_account)

        response_data = {
            'token': token.key,
            'fullname': saved_account.userprofile.full_name,
            'email': saved_account.email,
            'user_id': saved_account.id
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    """
    API endpoint for user login/authentication.

    POST /api/login/

    Authenticates users with email and password, returning an auth token
    upon successful login.

    Permissions:
        - AllowAny: No authentication required

    Returns:
        200: Login successful with token and user data
        400: Invalid credentials or validation errors
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request):
        """
        Handle user login request.

        Args:
            request: HTTP request containing login credentials

        Returns:
            Response: User token and profile information
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.get()

        token, created = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'fullname': user.userprofile.full_name,
            'email': user.email,
            'user_id': user.id
        }

        return Response(data)
