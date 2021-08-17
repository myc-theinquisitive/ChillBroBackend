from .helpers import  Point

def get_latitude_longitude(address_id):
    from Address.exportapi import get_latitude_longitude
    response = get_latitude_longitude(address_id)
    if response['is_valid']:
        point = Point(response['latitude'], response['longitude'])
        return point
    return None

def get_multiple_latitude_longitude(address_ids):
    from Address.exportapi import get_multiple_latitude_longitude
    response = get_multiple_latitude_longitude(address_ids)
    return list(map(lambda x: Point(x.latitude, x.longitude), response))