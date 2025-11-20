"""
用户URL配置
"""

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    UserProfileDetailView,
    PasswordChangeView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('me/password/', PasswordChangeView.as_view(), name='password-change'),
]
