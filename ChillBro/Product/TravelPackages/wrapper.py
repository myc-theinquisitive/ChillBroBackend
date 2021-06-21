from collections import defaultdict
from ..TravelPackageVehicle.export_apis import travel_package_id_wise_vehicles_count


def get_travel_package_id_wise_vehicles_count(travel_package_ids):
    return travel_package_id_wise_vehicles_count(travel_package_ids)


def get_place_id_wise_details(place_ids):
    from Product.Places.export_apis import get_place_details_for_ids
    places_data = get_place_details_for_ids(place_ids)

    place_id_wise_details = defaultdict(dict)
    for place in places_data:
        place_id_wise_details[place["id"]] = place

    return place_id_wise_details


def check_valid_place_ids(place_ids):
    from Product.Places.export_apis import get_all_place_ids
    all_place_ids = set(map(lambda x: x[0], get_all_place_ids()))
    invalid_place_ids = set(place_ids) - all_place_ids
    is_valid = True if len(invalid_place_ids) == 0 else False
    return is_valid, invalid_place_ids
