from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
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
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request):
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
