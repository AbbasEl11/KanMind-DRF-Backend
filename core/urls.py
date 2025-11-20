"""
Core URL configuration for KanMind project.

This module defines the main URL patterns for the entire project,
including the Django admin panel and API endpoints from all apps.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    
    # Authentication API endpoints (registration, login)
    # /api/registration/, /api/login/
    path('api/', include('auth_app.api.urls')),
    
    # Board API endpoints (CRUD, email check)
    # /api/boards/, /api/email-check/
    path('api/', include('boards_app.api.urls')),
    
    # Task and comment API endpoints
    # /api/tasks/, /api/tasks/{id}/comments/
    path('api/', include('tasks_app.api.urls')),
]
