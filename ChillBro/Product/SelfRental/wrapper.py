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


def check_distrance_price_self_rental_by_id(distance_price_ids, self_rental_id):
    from .models import DistancePrice
    distance_price_objects = DistancePrice.objects.filter(id__in=distance_price_ids,
                                                          self_rental_id=self_rental_id).values_list('id')
    if len(list(distance_price_objects)) != len(distance_price_ids):
        invalid_ids = set(distance_price_ids) - set(distance_price_objects)
        return False, list(invalid_ids)
    return True, []
