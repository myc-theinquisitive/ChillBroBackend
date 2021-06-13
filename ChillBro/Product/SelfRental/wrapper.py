from collections import defaultdict



def get_vehicle_data_by_id(vehicle_id):
    from ..Vehicle.export_apis import get_vehicle_details
    return get_vehicle_details(vehicle_id)


def get_vehicle_data_by_ids(vehicle_ids):
    from ..Vehicle.export_apis import get_vehicles_details
    return get_vehicles_details(vehicle_ids)


def get_vehicle_id_wise_details(vehicle_ids):
    vehicles_data = get_vehicle_data_by_ids(vehicle_ids)

    vehicle_type_id_wise_details = defaultdict(dict)
    for vehicle in vehicles_data:
        vehicle_type_id_wise_details[vehicle["id"]] = vehicle

    return vehicle_type_id_wise_details

def check_vehicle_exists_by_id(vehicle_id):
    from ..Vehicle.export_apis import check_vehicle_exists
    return check_vehicle_exists(vehicle_id)