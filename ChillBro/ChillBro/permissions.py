from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from UserApp.models import Employee, BusinessClient


class IsSuperAdminOrMYCEmployee(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        try:
            employee = Employee.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return False

        if employee.entity_id == "MYC":
            return True
        return False


class IsBusinessClient(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        try:
            business_client = BusinessClient.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return False


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.created_by_id != request.user.id:
            return False
        return True
