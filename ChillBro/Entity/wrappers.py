from Address.exportapi import create_address, get_address_details, update_address
from UserApp.exportapi import get_employee_details_for_entities
from collections import defaultdict


def post_create_address(address_data):
    return create_address(address_data)


def update_address_for_address_id(address_id, address_data):
    return update_address(address_id, address_data)


def get_total_products_count_in_entities(entity_ids):
    from Product.exportapi import total_products_count_in_entities
    return total_products_count_in_entities(entity_ids)

  
def get_address_details_for_address_ids(address_ids):
    return get_address_details(address_ids)


def get_entity_id_wise_employees(entity_ids):
    employees = get_employee_details_for_entities(entity_ids)
    entity_id_wise_employees = defaultdict(list)
    for employee in employees:
        entity_id_wise_employees[employee["entity_id"]].append(employee)
    return entity_id_wise_employees
