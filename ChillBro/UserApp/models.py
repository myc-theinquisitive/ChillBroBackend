from django.core.validators import MinLengthValidator
from django.db import models
from authentication.models import EmailUserManager, EmailAbstractUser
from .validations import validate_phone
from .constants import Roles
from .helpers import image_upload
import uuid



class MyUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField('Date of birth', null=True, blank=True)
    phone_number = models.CharField('phone_number', max_length=10, unique=True, null=True, blank=True,
                                    validators=[MinLengthValidator(10), validate_phone])

    # Required
    objects = EmailUserManager()


class BusinessClient(models.Model):
    business_name = models.CharField(max_length=100)
    secondary_contact = models.CharField(max_length=10, null=True, blank=True,
                                         validators=[MinLengthValidator(10), validate_phone])
    user_id = models.ForeignKey('MyUser', on_delete=models.CASCADE) 
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False,max_length=100)

class Employee(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False,max_length=100)
    entity_id = models.CharField(max_length=100)
    role = models.CharField(choices=[(role.name, role.value) for role in Roles],max_length=100)
    image = models.ImageField(upload_to=image_upload)
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey('MyUser', on_delete=models.CASCADE)
