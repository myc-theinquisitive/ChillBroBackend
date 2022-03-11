from django.db import models
from ChillBro.helpers import get_storage
from .helpers import image_upload_to_issue
from .constants import Departments, SupportStatus, EntityType
import uuid
from .helpers import get_user_model


def get_id():
    return str(uuid.uuid4())


class Issue(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id, verbose_name="Issue Id")
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)

    current_department = models.CharField(
        max_length=30, choices=[(department.name, department.value) for department in Departments],
        default=Departments.CUSTOMER_CARE.value)
    current_employee_id = models.CharField(max_length=36, blank=True, null=True)

    title = models.CharField(max_length=200)
    description = models.TextField()
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=30, choices=[(etype.name, etype.value) for etype in EntityType])
    order_id = models.CharField(max_length=36)
    product_id = models.CharField(max_length=36)
    support_status = models.CharField(
        max_length=30, choices=[(support_status.name, support_status.value) for support_status in SupportStatus],
        default=SupportStatus.TODO.value)
    final_resolution = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + " id - " + str(self.pk)


class IssueImage(models.Model):
    issue = models.ForeignKey("Issue", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_issue, storage=get_storage())

    def __str__(self):
        return "Issue Image - {0}".format(self.id)


class Transfer(models.Model):
    transferred_by = models.CharField(max_length=36)
    issue = models.ForeignKey("Issue", on_delete=models.CASCADE)
    employee_comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    transferred_to = models.CharField(
        max_length=100, choices=[(department.name, department.value) for department in Departments])
