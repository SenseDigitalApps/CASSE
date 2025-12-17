"""
URLs for authentication endpoints.
"""
from django.urls import path
from .views import LoginView, RegisterView, RefreshTokenView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('jwt/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
]

