import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .serializers import AddressSerializer
from .views import address_details_for_address_ids
import uuid


def create_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        serializer = valid_serializer.create(address_details)
        return {"is_valid": True, "address_id": serializer.id, "errors": None}
    else:
        return {"is_valid": False, "address_id": None, "errors": valid_serializer.errors}


def get_address_details(address_ids):
    return address_details_for_address_ids(address_ids)


def update_address(address_id, address_details):
    from .models import Address
    try:
        address = Address.objects.get(id=address_id)
    except ObjectDoesNotExist:
        return {"is_valid": False, "address_id": None, "errors": "Invalid Address Id"}

    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        serializer = valid_serializer.update(address, address_details)
        return {"is_valid": True, "address_id": serializer.id, "errors": None}
    else:
        return {"is_valid": False, "address_id": None, "errors": valid_serializer.errors}


def calculate_distance_between_two_points(point1, point2):
    p1_longitude = point1.longitude
    p1_latitude = point1.latitude
    p2_longitude = point2.longitude
    p2_latitude = point2.latitude
    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + p2_latitude + ',' + p2_longitude + '&key=' + settings.GMAPS_API_KEY)
    dic = response.json()
    distance = dic['rows'][0]['elements'][0]['distance']['value']
    duration = dic['rows'][0]['elements'][0]['duration']['value']
    return {'distance': distance, 'duration': duration}


def calculate_distance_between_multiple_points(source_point, destination_points):
    p1_longitude = source_point.longitude
    p1_latitude = source_point.latitude

    destinations_string = ''
    for point in destination_points:
        destinations_string += point.latitude + ',' + point.longitude + '|'

    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + destinations_string + '&key=' + settings.GMAPS_API_KEY)

    dic = response.json()

    all_distances = []
    for destination in dic['rows'][0]['elements']:
        distance = destination['distance']['value']
        duration = destination['duration']['value']
        all_distances.append({'distance': distance, 'duration': duration})
    return all_distances