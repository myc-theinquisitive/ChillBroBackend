from django.utils.text import slugify
import uuid


def upload_image_to_category(instance, filename):
    name = instance.category.name
    slug = slugify(name)
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/Category/%s/%s" % (slug, new_filename)


def update_image_to_category_icon(instance, filename):
    name = instance.name
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return "static/images/Category/icons/%s/%s" % (name, new_filename)
