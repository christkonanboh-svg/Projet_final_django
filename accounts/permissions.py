from rest_framework import permissions


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client


class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_agent


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user


class IsAgentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_agent or request.user.is_admin_user
        )


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user or request.user.is_agent:
            return True
        owner = getattr(obj, "client", None) or getattr(obj, "user", None)
        return owner == request.user
