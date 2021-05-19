from django.conf import settings
import uuid
from .constants import ActivationStatus


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def get_entity_status(statuses):
    all_statuses = [each_entity.value for each_entity in ActivationStatus]
    if len(statuses) == 0:
        return all_statuses
    return statuses


def upload_image_for_entity(instance, filename, type):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/entity/%s/%s/%s" % (id, type, new_filename)


def upload_pan_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "pan")


def upload_registration_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "registration")


def upload_gst_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "gst")


def upload_aadhar_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "aadhar")


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"
