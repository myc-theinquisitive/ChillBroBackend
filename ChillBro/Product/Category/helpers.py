from django.utils.text import slugify
import uuid


def image_upload_to_category(instance, filename):
    name = instance.category.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/Category/%s/%s" % (slug, new_filename)

