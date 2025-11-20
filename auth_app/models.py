"""
Authentication app models.

This module defines the UserProfile model that extends Django's built-in User model
with additional profile information.
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile model.
    
    Extends Django's default User model with additional profile information.
    Each User has exactly one UserProfile through a one-to-one relationship.
    
    Attributes:
        user (User): One-to-one relationship with Django's User model
        full_name (str): User's full display name (max 100 characters)
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="Associated user account"
    )
    full_name = models.CharField(
        max_length=100,
        help_text="User's full display name"
    )
    
    def __str__(self):
        """Return string representation of the user profile."""
        return f"{self.full_name} ({self.user.username})"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
