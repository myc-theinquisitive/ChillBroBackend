from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from UserApp.models import Employee, BusinessClient
from Entity.models import BusinessClientEntity
from Product.models import SellerProduct
from django.conf import settings


def get_myc_id():
    return settings.MYC_ID if hasattr(settings, 'MYC_ID') else "MYC"


class IsSuperAdminOrMYCEmployee(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        try:
            employee = Employee.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return False

        if employee.entity_id == get_myc_id():
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


class IsEmployee(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        try:
            employee = Employee.objects.get(user_id=user.id)
            if not employee.is_active:
                return False
        except ObjectDoesNotExist:
            return False
        return True


class IsGet(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return False


class IsBusinessClientEntity(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            entity_id = request.data['entity_id']
        except:
            return True

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id, business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        entity_id = obj.id

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id, business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class IsBusinessClientEntityById(permissions.BasePermission):

    def has_object_permission(self, request, view, id):
        user = request.user
        entity_id = id

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id, business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class IsBusinessClientEntities(permissions.BasePermission):

    def has_object_permission(self, request, view, ids):
        user = request.user
        entity_ids = ids

        entities = BusinessClientEntity.objects.filter(entity_id__in=entity_ids, business_client_id=user.id)
        if len(entities) == len(entity_ids):
            return True
        return False


class IsEmployeeEntities(permissions.BasePermission):

    def has_object_permission(self, request, view, ids):
        user = request.user
        entity_id = ids
        if len(entity_id) != 1:
            return False
        employee = Employee.objects.filter(entity_id__in=entity_id, user_id=user.id)
        if not employee.is_active:
            return False
        if len(employee) == 1:
            return True
        return False


class IsEmployeeEntityById(permissions.BasePermission):

    def has_object_permission(self, request, view, id):
        user = request.user
        entity_id = id

        try:
            employee = Employee.objects.get(entity_id=entity_id, user_id=user.id)
            if not employee.is_active:
                return False
        except ObjectDoesNotExist:
            return False
        return True


class IsEmployeeEntity(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        entity_id = obj.id

        try:
            employee = Employee.objects.get(entity_id=entity_id, user_id=user.id)
            if not employee.is_active:
                return False
        except ObjectDoesNotExist:
            return False
        return True


class IsSellerProduct(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        product_id = obj

        try:
            entity = SellerProduct.objects.get(product_id=product_id)
        except ObjectDoesNotExist:
            return False

        if IsBusinessClientEntity().has_object_permission(request, view, entity):
            return True

        if IsEmployeeEntity().has_object_permission(request, view, entity):
            return True

        return False


class IsBookingBusinessClient(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        booking = obj
        entity_id = booking.entity_id

        try:
            business_client = BusinessClientEntity.objects.get(entity_id=entity_id, business_client_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class IsBookingEmployee(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        booking = obj
        entity_id = booking.entity_id

        try:
            employee = Employee.objects.get(entity_id=entity_id, user_id=user.id)
            if not employee.is_active:
                return False
        except ObjectDoesNotExist:
            return False
        return True


class IsBusinessClientEmployee(permissions.BasePermission):

    def has_object_permission(self, request, view, id):
        user = request.user
        employee_id = id

        try:
            entity_id = Employee.objects.get(id=employee_id)
            business_client = BusinessClient.objects.get(entity_id=entity_id, user_id=user.id)
        except ObjectDoesNotExist:
            return False
        return True


class IsEmployeeBusinessClient(permissions.BasePermission):
    def has_object_permission(self, request, view, business_client_id):
        user = request.user

        try:
            business_client_entities = BusinessClientEntity.objects.get(
                business_client_id=business_client_id).values_list('entity_id')
            employee = Employee.objects.get(entity_id__in=business_client_entities)
        except ObjectDoesNotExist:
            return False
        return True
