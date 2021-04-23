from django.conf import settings
from django.utils.text import slugify
import uuid
from django.shortcuts import get_object_or_404

def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload(instance, filename, type):
    name = instance.id
    slug = slugify(name)
    # basename, file_extension = filename.split(".")
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/entity/%s/%s/%s" % (type, slug, new_filename)


def image_upload_pan(instance, filename):
    return image_upload(instance, filename, "pan")


def image_upload_registration(instance, filename):
    return image_upload(instance, filename, "registration")


def image_upload_gst(instance, filename):
    return image_upload(instance, filename, "gst")


def image_upload_aadhar(instance, filename):
    return image_upload(instance, filename, "aadhar")
