"""
URLs for user management endpoints.
"""
from django.urls import path
from .views import (
    UserMeView,
    UserListView,
    UserDetailView,
    UserSuspendView,
    UserActivateView,
)

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('', UserListView.as_view(), name='user-list'),
    path('<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('<uuid:id>/suspend/', UserSuspendView.as_view(), name='user-suspend'),
    path('<uuid:id>/activate/', UserActivateView.as_view(), name='user-activate'),
]

