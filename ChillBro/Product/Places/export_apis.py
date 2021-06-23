def get_place_details(place_id):
    from .views import PlaceView
    return PlaceView().get(place_id)


def get_place_details_for_ids(place_ids):
    from .views import PlaceView
    return PlaceView().get_by_ids(place_ids)

def get_invalid_place_ids(place_ids):
    from .models import Place

    all_place_ids = Place.objects.all().values_list('id',flat=True)
    invalid_place_ids = set(place_ids) - set(all_place_ids)
    is_valid = True if len(invalid_place_ids) == 0 else False
    return is_valid, invalid_place_ids