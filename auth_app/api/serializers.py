from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth.models import User
from django.utils.text import slugify


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True, max_length=100)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email',
                  'repeated_password', 'fullname']
        read_only_fields = ['username']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        fullname = self.validated_data.pop('fullname')
        username_slug = slugify(fullname)

        if pw != repeated_pw:
            raise serializers.ValidationError(
                {"error": "Passwords do not match."})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError(
                {"error": "Email already in use."})

        if User.objects.filter(username=username_slug).exists():
            raise serializers.ValidationError(
                {"error": "username already in use."})

        user = User(
            email=self.validated_data['email'], username=username_slug)
        user.set_password(pw)
        user.save()
        UserProfile.objects.create(user=user, full_name=fullname)
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "Invalid Email."})
        return value

    def get(self):
        email = self.validated_data['email']
        password = self.validated_data['password']

        user = User.objects.get(email=email)

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"error": "Invalid password."})

        return user
