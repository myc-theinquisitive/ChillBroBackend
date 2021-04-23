from django.utils.text import slugify
import uuid
from django.shortcuts import get_object_or_404


def image_upload(instance, filename):
    name = instance.id
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/employee/%s/%s" % (slug, new_filename)