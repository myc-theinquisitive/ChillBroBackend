from django.utils.text import slugify
import uuid
from django.shortcuts import get_object_or_404


def image_upload_to_issue(instance, filename):
    name = instance.issue.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/issue/%s/%s" % (slug, new_filename)