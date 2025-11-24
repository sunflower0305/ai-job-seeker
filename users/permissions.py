"""
用户权限控制
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问
    """
    message = '只有管理员才能访问此资源'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsNormalUser(permissions.BasePermission):
    """
    只允许普通用户访问
    """
    message = '只有普通用户才能访问此资源'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'user'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    允许资源所有者或管理员访问
    """
    message = '您没有权限访问此资源'

    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有资源
        if request.user.role == 'admin':
            return True

        # 检查对象是否有user属性
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # 如果对象本身就是user
        return obj == request.user
