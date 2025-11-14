from django.urls import path, include
from .views import BoardViewSet, EmailCheck
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('email-check/', EmailCheck.as_view(), name='email-check'),
    path('', include(router.urls)),

]
