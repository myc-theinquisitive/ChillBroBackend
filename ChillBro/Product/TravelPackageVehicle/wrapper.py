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
        vehicle_type_id_wise_details[vehicle["product"]] = vehicle

    return vehicle_type_id_wise_details
    

def get_travel_package_data_by_id(travel_package_id, start_time):
    from ..TravelPackages.export_apis import get_travel_package_details
    return get_travel_package_details(travel_package_id, start_time)
    
    
def get_travel_package_data_by_ids(travel_package_ids):
    from ..TravelPackages.export_apis import get_travel_package_details_by_ids
    travel_packages_data = get_travel_package_details_by_ids(travel_package_ids)
    print(travel_packages_data,"travel_packages_data")
    
    travel_package_id_wise_details = defaultdict(dict)
    for travel_package in travel_packages_data:
        travel_package_id_wise_details[travel_package["id"]] = travel_package

    return travel_package_id_wise_details
