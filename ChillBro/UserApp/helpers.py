import uuid
from django.shortcuts import get_object_or_404


def upload_employee_image(instance, filename):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/employee/%s/%s" % (id, new_filename)