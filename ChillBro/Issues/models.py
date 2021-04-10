from django.utils import timezone
from django.db import models
# Create your models here.
from .helpers import image_upload_to_issue
from .validators import checkProductId, checkOrderId
from .wrappers import Departments
from .constants import Status


class Issue(models.Model):
    user_id = models.CharField(max_length=100)
    current_department = models.CharField(max_length=100, choices=[(department.name, department.value) for department in Departments], default=Departments.CUSTOMER_CARE.value)
    current_employeeId = models.CharField(max_length=100, blank=True, null=True)
    issue_title = models.CharField(max_length=200)
    description = models.TextField()
    entity = models.CharField(max_length=30)
    order_id = models.CharField(max_length=30, validators=[checkOrderId])
    product_id = models.CharField(max_length=30, validators=[checkProductId])
    status = models.CharField(max_length=20,choices=[(status.name, status.value) for status in Status], default=Status.TODO.value)
    final_resolution = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.issue_title + " id - " + str(self.pk)


class IssueImage(models.Model):
    issue_id = models.ForeignKey("Issue", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_issue)

    def __str__(self):
        return "Issue Image - {0}".format(self.id)


class Transfer(models.Model):
    employee_id = models.CharField(max_length=30)
    issue_id = models.ForeignKey("Issue", on_delete=models.CASCADE)
    employee_comment = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    transferred_to = models.CharField(max_length=100, choices=[(department.name, department.value) for department in Departments])
