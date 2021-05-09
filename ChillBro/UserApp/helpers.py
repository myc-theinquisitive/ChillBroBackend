import uuid


def upload_employee_image(instance, filename):
    id = instance.employee.id
    file_extension = filename.split(".")[-1]
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/employee/%s/%s" % (id, new_filename)
