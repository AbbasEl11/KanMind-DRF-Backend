"""
Task app admin configuration.

Django admin site configuration for task and comment management.
"""

from django.contrib import admin
from .models import Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model.
    
    Provides comprehensive task management with filtering, searching,
    and organized field display.
    """
    
    list_display = [
        'id', 'title', 'board', 'status', 'priority', 
        'assignee', 'reviewer', 'due_date'
    ]
    list_filter = ['status', 'priority', 'board', 'due_date']
    search_fields = ['title', 'description', 'board__title']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'board', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assignee', 'reviewer')
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """
    Admin interface for TaskComment model.
    
    Provides comment management with task context and timestamp display.
    """
    
    list_display = ['id', 'task', 'author', 'created_at', 'content_preview']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'task__title', 'author__username']
    readonly_fields = ['id', 'created_at']
    
    def content_preview(self, obj):
        """Display first 50 characters of comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'