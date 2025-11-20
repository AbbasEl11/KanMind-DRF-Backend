"""
Authentication app admin configuration.

Django admin site configuration for authentication-related models.
Currently using default admin interface without customization.
"""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    
    Displays user profiles with their associated Django user accounts
    and full names for easy management.
    """
    
    list_display = ['user', 'full_name']
    search_fields = ['full_name', 'user__username', 'user__email']
    list_filter = ['user__date_joined']
    readonly_fields = ['user']
