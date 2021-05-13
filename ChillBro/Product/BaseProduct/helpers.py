from django.utils.text import slugify
import uuid
from django.conf import settings


def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload_to_product(instance, filename):
    name = instance.product.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/Product/%s/%s" % (slug, new_filename)
