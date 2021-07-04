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


def validate_place_ids(place_ids):
    from Product.Places.export_apis import get_invalid_place_ids
    return get_invalid_place_ids(place_ids)
