from collections import defaultdict


def get_vehicle_type_data_by_id(vehicle_type_id):
    from ..Vehicle.export_apis import get_vehicle_type_details
    return get_vehicle_type_details(vehicle_type_id)


def get_vehicle_types_data_by_ids(vehicle_type_ids):
    from ..Vehicle.export_apis import get_vehicle_types_details
    return get_vehicle_types_details(vehicle_type_ids)


def get_vehicle_type_id_wise_details(vehicle_type_ids):
    vehicle_types_data = get_vehicle_types_data_by_ids(vehicle_type_ids)

    vehicle_type_id_wise_details = defaultdict(dict)
    for vehicle_type in vehicle_types_data:
        vehicle_type_id_wise_details[vehicle_type["id"]] = vehicle_type

    return vehicle_type_id_wise_details
