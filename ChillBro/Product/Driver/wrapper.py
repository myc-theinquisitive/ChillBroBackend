from Address.exportapi import create_address, get_address_details, update_address
from collections import defaultdict


def get_vehicle_type_data_by_id(vehicle_type_id):
    from ..VehicleTypes.export_apis import get_vehicle_type_details
    return get_vehicle_type_details(vehicle_type_id)


def get_vehicle_types_data_by_ids(vehicle_type_ids):
    from ..VehicleTypes.export_apis import get_vehicle_types_details
    return get_vehicle_types_details(vehicle_type_ids)


def get_vehicle_type_id_wise_details(vehicle_type_ids):
    vehicle_types_data = get_vehicle_types_data_by_ids(vehicle_type_ids)

    vehicle_type_id_wise_details = defaultdict(dict)
    for vehicle_type in vehicle_types_data:
        vehicle_type_id_wise_details[vehicle_type["id"]] = vehicle_type

    return vehicle_type_id_wise_details


def post_create_address(address_data):
    return create_address(address_data)


def update_address_for_address_id(address_id, address_data):
    return update_address(address_id, address_data)


def get_address_details_for_address_ids(address_ids):
    return get_address_details(address_ids)
