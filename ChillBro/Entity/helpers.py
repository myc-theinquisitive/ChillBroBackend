from django.conf import settings
import uuid
from .constants import ActivationStatus, EntityType
from django.utils.text import slugify
import requests


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_entity_status(statuses):
    all_statuses = [each_entity.value for each_entity in ActivationStatus]
    if len(statuses) == 0:
        return all_statuses
    return statuses


def upload_image_for_entity(instance, filename):
    id = instance.entity_id
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/entity/%s/%s" % (id, new_filename)


def upload_image_for_entity_type(instance, filename, type):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/entity/%s/%s/%s" % (id, type, new_filename)


def image_upload_to_amenities(instance, filename):
    name = instance.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/Amenities/%s/%s" % (slug, new_filename)


def upload_pan_image_for_entity(instance, filename):
    return upload_image_for_entity_type(instance, filename, "pan")


def upload_registration_image_for_entity(instance, filename):
    return upload_image_for_entity_type(instance, filename, "registration")


def upload_gst_image_for_entity(instance, filename):
    return upload_image_for_entity_type(instance, filename, "gst")


def upload_aadhar_image_for_entity(instance, filename):
    return upload_image_for_entity_type(instance, filename, "aadhar")


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_entity_types_filter(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) == 0:
        return entities
    return entity_filter


class LatLong:
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude


def calculate_distance_between_two_points(point1, point2):
    p1_longitude = point1.longitude
    p1_latitude = point1.latitude
    p2_longitude = point2.longitude
    p2_latitude = point2.latitude
    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + p2_latitude + ',' + p2_longitude + '&key=' + settings.GMAPS_API_KEY)
    dic = response.json()
    print(dic)
    distance = dic['rows'][0]['elements'][0]['distance']['value']
    duration = dic['rows'][0]['elements'][0]['duration']['value']
    return {'distance': distance, 'duration': duration}


def calculate_distance_between_multiple_points(source_point, destination_points):
    p1_longitude = source_point.longitude
    p1_latitude = source_point.latitude

    entity_ids = list(map(lambda x: x[0], destination_points))

    destinations_string = ''
    for entity_id, point in destination_points:
        destinations_string += point.latitude + ',' + point.longitude + '|'

    response = requests.get(
        'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + p1_latitude + ',' + p1_longitude + '&destinations=' + destinations_string + '&key=' + settings.GMAPS_API_KEY)

    dic = response.json()

    all_distances = {}
    count = 0
    for destination in dic['rows'][0]['elements']:
        distance = destination['distance']['value']
        duration = destination['duration']['value']
        # all_distances.append({'distance': distance, 'duration': duration})
        all_distances[entity_ids[count]] = {'distance': distance, 'duration': duration}
        count += 1
    print(all_distances, '========================= all_distances ====================================')
    return all_distances
