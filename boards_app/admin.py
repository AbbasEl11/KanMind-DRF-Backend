"""
Board app admin configuration.

Django admin site configuration for board management.
"""

from django.contrib import admin
from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface for Board model.
    
    Provides board management with owner, member, and task count display.
    Allows searching and filtering by various criteria.
    """
    
    list_display = ['id', 'title', 'owner', 'get_member_count', 'get_task_count']
    search_fields = ['title', 'owner__username']
    list_filter = ['owner']
    filter_horizontal = ['members']  # Better UI for many-to-many fields
    readonly_fields = ['id']
    
    def get_member_count(self, obj):
        """Display number of board members."""
        return obj.members.count()
    get_member_count.short_description = 'Members'
    
    def get_task_count(self, obj):
        """Display number of tasks on board."""
        return obj.task_set.count()
    get_task_count.short_description = 'Tasks'
