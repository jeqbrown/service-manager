from rest_framework import permissions

class CustomerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        elif request.method == 'DELETE':
            return request.user.is_superuser
        else:
            return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        elif request.method == 'DELETE':
            return request.user.is_superuser
        else:
            return request.user.is_staff
