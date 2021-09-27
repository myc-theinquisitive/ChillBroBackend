import requests
from django.conf import settings
from .BaseProduct.constants import ActivationStatus


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_status(statuses):
    all_statuses = [each_status.value for each_status in ActivationStatus]
    if len(statuses) == 0:
        return all_statuses
    return statuses


def calculate_distance_between_two_points(point1, point2):
    p1_longitude = point1.longitude
    p1_latitude = point1.latitude
    p2_longitude = point2.longitude
    p2_latitude = point2.latitude
    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + p2_latitude + ',' + p2_longitude + '&key=AIzaSyAv_fCi15SFyut7jTvkPJE3bmdU0MJ-Mos')
    dic = response.json()
    print(dic)
    distance = dic['rows'][0]['elements'][0]['distance']['value']
    duration = dic['rows'][0]['elements'][0]['duration']['value']
    return {'distance': distance, 'duration': duration}


def calculate_distance_between_multiple_points(source_point, destination_points):
    p1_longitude = source_point.longitude
    p1_latitude = source_point.latitude

    product_ids = list(map(lambda x: x[0], destination_points))

    destinations_string = ''
    for product_id, point in destination_points:
        destinations_string += point.latitude + ',' + point.longitude + '|'

    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + destinations_string + '&key=AIzaSyAv_fCi15SFyut7jTvkPJE3bmdU0MJ-Mos')

    print(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + destinations_string + '&key=AIzaSyAv_fCi15SFyut7jTvkPJE3bmdU0MJ-Mos,',
        'url')
    dic = response.json()

    all_distances = {}
    count=0
    for destination in dic['rows'][0]['elements']:
        distance = destination['distance']['value']
        duration = destination['duration']['value']
        all_distances[product_ids[count]] = {'distance': distance, 'duration': duration}
        count+=1
    print(all_distances,'========================= all_distances ====================================')
    return all_distances
