from django.conf import settings
import uuid
from .constants import *
from ChillBro.helpers import get_time_period, get_previous_time_period


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_user_id_proof(instance, filename):
    id = instance.booking.id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/users_id_proof/%s/%s" % (id, new_filename)


def image_upload_to_check_in(instance, filename):
    id = instance.check_in.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/check_in/%s/%s" % (id, new_filename)


def image_upload_to_check_out(instance, filename):
    id = instance.check_out.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/check_out/%s/%s" % (id, new_filename)


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_entity_types_filter(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) == 0:
        return entities
    return entity_filter


def get_status_filters(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status
