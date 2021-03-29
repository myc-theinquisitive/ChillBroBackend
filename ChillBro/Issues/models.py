from django.utils import timezone
from django.db import models
# Create your models here.
from .helpers import image_upload_to_product, department_choices,getEntityByProductId,getUserId
from .validators import checkProductId,checkOrderId

class Issue(models.Model):
    user_id=models.CharField(max_length=100,default=getUserId)
    current_department=models.IntegerField(max_length=100,choices=department_choices,default=1)
    current_emplooyeId=models.CharField(max_length=100,blank=True,null=True)
    issue_title=models.CharField(max_length=200)
    description=models.TextField(max_length=1000)
    entity=models.CharField(max_length=30,blank=True,null=True,default="getEntityByProductId")
    order_id=models.CharField(max_length=30,validators=[checkOrderId])
    product_id=models.CharField(max_length=30,validators=[checkProductId])
    status_choices=((1,"ToDo"),(2,"In Progress"),(3,"Done"))
    status=models.IntegerField(choices=status_choices,default=1)
    final_resolution=models.CharField(max_length=200,blank=True,null=True)
    created_at=models.DateTimeField(default=timezone.now)
    updated_at=models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.issue_title+" id - "+str(self.pk)



class IssueImage(models.Model):
    issue_id = models.ForeignKey("Issue", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_product)

    def __str__(self):
        return "Issue Image - {0}".format(self.id)

class Transfer(models.Model):
    emplooye_id=models.CharField(max_length=30)
    issue_id=models.ForeignKey("Issue",on_delete=models.CASCADE)
    emplooye_comment=models.CharField(max_length=200)
    created_at=models.DateTimeField(default=timezone.now)
    updated_at=models.DateTimeField(blank=True,null=True)
    # status_choices = ((1, "ToDo"), (2, "In Progress"), (3, "Done"))
    # status = models.IntegerField(choices=status_choices, default=1)
    department=models.CharField(max_length=100,choices=department_choices)