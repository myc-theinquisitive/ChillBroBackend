from django.conf import settings
from django.utils.text import slugify
import uuid
from django.shortcuts import get_object_or_404

def get_user_model():
    return settings.AUTH_USER_MODEL


def upload_image_for_entity(instance, filename, type):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/entity/%s/%s/%s" % (type, id, new_filename)


def upload_pan_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "pan")


def upload_registration_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "registration")


def upload_gst_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "gst")


def upload_aadhar_image_for_entity(instance, filename):
    return upload_image_for_entity(instance, filename, "aadhar")
