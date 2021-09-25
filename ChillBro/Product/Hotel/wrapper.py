from .helpers import LatLong


def get_latitude_longitude(address_id):
    from Address.exportapi import get_latitude_longitude
    response = get_latitude_longitude(address_id)
    if response['is_valid']:
        point = LatLong(response['latitude'], response['longitude'])
        return point
    return None


def format_multiple_latitude_longitude(addresses):
    return list(map(lambda x: LatLong(x.latitude, x.longitude), addresses))
