from django.core.exceptions import ObjectDoesNotExist

from .models import BusinessClient, Employee


def get_employee_details_for_entities(entity_ids):
    from .views import get_employee_details_for_entity_ids
    return get_employee_details_for_entity_ids(entity_ids)


def check_valid_business_client(user):
    try:
        business_client = BusinessClient.objects.get(user_id=user.id)
    except ObjectDoesNotExist:
        return False
    return True


def check_valid_employee(user):
    try:
        employee = Employee.objects.get(user_id=user.id)
        if not employee.is_active:
            return False
    except ObjectDoesNotExist:
        return False
    return True


def entity_ids_for_employee(employee_id):
    try:
        employee = Employee.objects.get(user_id=employee_id)
        if employee.is_active:
            return [employee.entity_id]
    except ObjectDoesNotExist:
        return []

    return []
