"""
Board API URL configuration.

Defines URL patterns for board management and email lookup endpoints.
Uses DRF Router for automatic ViewSet URL generation.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, EmailCheck


# Router for board CRUD operations
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    # Email lookup endpoint for finding users to add as board members
    path('email-check/', EmailCheck.as_view(), name='email-check'),
    
    # Board endpoints (list, create, retrieve, update, delete)
    # /api/boards/ - GET (list), POST (create)
    # /api/boards/{id}/ - GET (retrieve), PUT/PATCH (update), DELETE (delete)
    path('', include(router.urls)),
]
