from django.conf import settings
import uuid


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def upload_image_for_employee_type(instance, filename, type):
    id = instance.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s.%s" % (str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/myc/employee/%s/%s/%s" % (id, type, new_filename)


def upload_pan_image_for_employee(instance, filename):
    return upload_image_for_employee_type(instance, filename, "pan")


def upload_aadhar_image_for_employee(instance, filename):
    return upload_image_for_employee_type(instance, filename, "aadhar")
