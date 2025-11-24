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
    AdminUserManagementView,
    AdminUserDetailView,
    admin_statistics_view,
    admin_analytics_view,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/profile/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('me/password/', PasswordChangeView.as_view(), name='password-change'),

    # 管理员API
    path('admin/users/', AdminUserManagementView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/statistics/', admin_statistics_view, name='admin-statistics'),
    path('admin/analytics/', admin_analytics_view, name='admin-analytics'),
]
