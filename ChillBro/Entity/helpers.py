from django.conf import settings
import uuid
from .constants import ActivationStatus, EntityType
from django.utils.text import slugify
import requests
from Address.helpers import calculate_distance_between_multiple_points


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


def calculate_distance_between_location_multiple_entities(source_point, destinations):
    entity_ids = list(map(lambda x: x[0], destinations))
    destination_points = list(map(lambda x: x[1], destinations))
    distance_response = calculate_distance_between_multiple_points(source_point, destination_points)

    all_distances = {}
    count = 0
    for distance_data in distance_response:
        distance = distance_data['distance']
        duration = distance_data['duration']
        all_distances[entity_ids[count]] = {'distance': distance, 'duration': duration}
        count += 1
    return all_distances
