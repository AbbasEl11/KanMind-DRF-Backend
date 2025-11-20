"""
Authentication API URL configuration.

Defines URL patterns for user registration and login endpoints.
"""

from django.urls import path
from .views import RegistrationView, LoginView


urlpatterns = [
    # User registration endpoint
    path('registration/', RegistrationView.as_view(), name='registration'),
    
    # User login endpoint
    path('login/', LoginView.as_view(), name='login'),
]
