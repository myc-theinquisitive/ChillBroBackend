import requests
from django.conf import settings
from .constants import DISTANCE_MATRIX_SINGLE_POINT_URL, DISTANCE_MATRIX_MULTI_POINT_URL
import uuid


def upload_image_to_city_icon(instance, filename):
    name = instance.name
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/Cities/%s/%s" % (name, new_filename)


def calculate_distance_between_two_points(point1, point2):
    response = requests.get(
        DISTANCE_MATRIX_SINGLE_POINT_URL.format(point1.latitude, point1.longitude, point2.latitude,
                                                point2.longitude, settings.GMAPS_API_KEY))
    dic = response.json()
    distance = dic['rows'][0]['elements'][0]['distance']['value']
    duration = dic['rows'][0]['elements'][0]['duration']['value']
    return {'distance': distance, 'duration': duration}


def calculate_distance_between_multiple_points(source_point, destination_points):
    destinations_string = ''
    for point in destination_points:
        destinations_string += point.latitude + ',' + point.longitude + '|'

    response = requests.get(
        DISTANCE_MATRIX_MULTI_POINT_URL.format(source_point.latitude, source_point.longitude,
                                               destinations_string, settings.GMAPS_API_KEY))
    dic = response.json()
    all_distances = []
    for destination in dic['rows'][0]['elements']:
        distance = destination['distance']['value']
        duration = destination['duration']['value']
        all_distances.append({'distance': distance, 'duration': duration})
    return all_distances
