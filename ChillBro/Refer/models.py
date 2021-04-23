from django.db import models
from .validations import validate_phone
from django.core.validators import MinLengthValidator
import uuid
# Create your models here.

class ReferBusinessClient(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False,max_length=100)
    business_type = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    primary_contact = models.CharField(max_length=10,validators=[MinLengthValidator(10),validate_phone])
    secondary_contact = models.CharField(max_length=100,validators=[MinLengthValidator(10),validate_phone])
    address = models.TextField()