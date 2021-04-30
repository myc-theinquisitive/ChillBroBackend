from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from UserApp.models import Employee, BusinessClient
from Entity.models import BusinessClientEntity
from Product.models import SellerProduct

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

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.created_by_id != request.user.id:
            return False
        return True

class IsUserOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user_id_id != request.user.id:
            return False
        return True

class IsBookingOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user_id != request.user.id:
            return False
        return True

class IsReviewOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.reviewed_by_id != request.user.id:
            return False
        return True

class IsOwnerById(permissions.BasePermission):

    def has_object_permission(self, request, view, id):
        if id != request.user.id:
            return False
        return True


class IsBusinessClient(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        try:
            business_client = BusinessClient.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class IsGet(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return False


class CheckBusinessClientEntity(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            entity_id = request.data['entity_id']
        except:
            return True

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id,business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        entity_id = obj.id

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id,business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True

class CheckBusinessClientEntityById(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        entity_id = obj

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id,business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class CheckSellerProduct(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        product_id = obj

        try:
            business_client = SellerProduct.objects.get(product_id=product_id,seller_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True
