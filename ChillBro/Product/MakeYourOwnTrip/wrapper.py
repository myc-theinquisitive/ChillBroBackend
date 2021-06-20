from collections import defaultdict


def get_place_id_wise_details(place_ids):
    from Product.Places.export_apis import get_place_details_for_ids
    places_data = get_place_details_for_ids(place_ids)

    place_id_wise_details = defaultdict(dict)
    for place in places_data:
        place_id_wise_details[place["id"]] = place

    return place_id_wise_details
