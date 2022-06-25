from rest_framework import permissions


class IsUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if request.user.is_authenticated and (
            user.is_user or request.user.is_superuser
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_user and not request.user.is_superuser:
            return obj.author == request.user
        return False


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if request.user.is_authenticated and (
            user.is_admin or request.user.is_superuser
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin or request.user.is_superuser:
            return True
        return False


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
