from django.utils.text import slugify
import uuid
from django.conf import settings


def upload_image_to_place(instance, filename):
    name = instance.place.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/place/%s/%s" % (slug, new_filename)
