from collections import defaultdict


def get_basic_driver_data_by_id(driver_id):
    from ..Driver.export_apis import get_basic_driver_details
    return get_basic_driver_details(driver_id)


def get_basic_driver_data_by_ids(driver_ids):
    from ..Driver.export_apis import get_basic_drivers_details
    return get_basic_drivers_details(driver_ids)


def get_basic_driver_id_wise_details(driver_ids):
    drivers_data = get_basic_driver_data_by_ids(driver_ids)
    print("drivers data",drivers_data)
    driver_type_id_wise_details = defaultdict(dict)
    for driver in drivers_data:
        print(driver)
        driver_type_id_wise_details[driver["driver_id"]] = driver

    return driver_type_id_wise_details


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
