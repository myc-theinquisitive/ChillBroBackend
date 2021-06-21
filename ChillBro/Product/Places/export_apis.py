def get_place_details(place_id):
    from .views import PlaceView
    return PlaceView().get(place_id)


def get_place_details_for_ids(place_ids):
    from .views import PlaceView
    return PlaceView().get_by_ids(place_ids)

def get_all_place_ids():
    from .models import Place
    return Place.objects.all().values_list('id')