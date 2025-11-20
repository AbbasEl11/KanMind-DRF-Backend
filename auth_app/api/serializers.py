"""
Authentication API serializers.

This module contains serializers for user registration and login functionality.
"""

from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import serializers
from auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles new user account creation with username auto-generation from full name,
    password validation, and user profile creation.
    
    Fields:
        username (str): Auto-generated from fullname (read-only in response)
        password (str): User password (write-only)
        email (str): User email address (must be unique)
        repeated_password (str): Password confirmation (write-only)
        fullname (str): User's full name for profile (write-only)
    """
    
    fullname = serializers.CharField(
        write_only=True, 
        max_length=100,
        help_text="User's full display name"
    )
    repeated_password = serializers.CharField(
        write_only=True,
        help_text="Password confirmation"
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'repeated_password', 'fullname']
        read_only_fields = ['username']
        extra_kwargs = {'password': {'write_only': True}}
        
        # Validate email uniqueness
    def validate_email(self, value):
                
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "Email already in use."})
        return value
          # Validate password match  
    def validate_fullname(self, value):
        slug = slugify(value)
        if User.objects.filter(username=slug).exists():
            raise serializers.ValidationError(
                {"error": "username already in use."})
        return value
    # Validate password match
    def validate_password(self, value):
        pw = value
        repeated_pw = "repeated_password"
        
        if pw != repeated_pw:
            raise serializers.ValidationError(
                {"error": "Passwords do not match."})
        return value
                
    def save(self):
        """
        Create and save a new user with associated profile.
        
        - Validates password match
        - Checks email uniqueness
        - Generates username from fullname using slugify
        - Creates UserProfile with full_name
        
        Returns:
            User: The newly created user instance
        
        """
        pw = self.validated_data['password']

        fullname = self.validated_data.pop('fullname')
        username_slug = slugify(fullname)
        
        # Create user and profile
        user = User(
            email=self.validated_data['email'], 
            username=username_slug
        )
        user.set_password(pw)
        user.save()
        UserProfile.objects.create(user=user, full_name=fullname)
        
        return user


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login/authentication.
    
    Validates user credentials using email and password.
    
    Fields:
        email (str): User's email address
        password (str): User's password (write-only)
    """
    
    email = serializers.EmailField(
        help_text="User's email address"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="User's password"
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, value):
        """
        Validate that the email exists in the database.
        
        Args:
            value (str): Email address to validate
            
        Returns:
            str: Validated email address
            
        Raises:
            ValidationError: If email doesn't exist
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "Invalid Email."})
        return value

    def get(self):
        """
        Authenticate user with email and password.
        
        Returns:
            User: Authenticated user instance
            
        Raises:
            ValidationError: If password is incorrect
        """
        email = self.validated_data['email']
        password = self.validated_data['password']

        user = User.objects.get(email=email)

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"error": "Invalid password."})

        return user
