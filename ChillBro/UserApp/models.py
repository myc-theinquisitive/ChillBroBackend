from django.core.validators import MinLengthValidator
from django.db import models
from ChillBro.validations import validate_email
from ChillBro.helpers import get_storage
from authentication.models import EmailUserManager, EmailAbstractUser
from .validations import validate_phone
from .helpers import upload_employee_image
import uuid
from .constants import GenderTypes


class MyUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField(verbose_name='Date of birth', null=True, blank=True)
    phone_number = models.CharField(verbose_name='phone_number', max_length=10, unique=True, null=True, blank=True,
                                    validators=[MinLengthValidator(10), validate_phone])
    gender = models.CharField(choices=[(gender.name, gender.value) for gender in GenderTypes], max_length=36)
    backup_phone_number = models.CharField(verbose_name='backup_phone_number', max_length=10, unique=True,
                                           null=True, blank=True, validators=[MinLengthValidator(10), validate_phone])
    backup_email = models.CharField(verbose_name='backup_email', max_length=30, unique=True, null=True, blank=True,
                                    validators=[validate_email])
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)

    # Required
    objects = EmailUserManager()


# TODO: Add created at and created by for business client and employee
class BusinessClient(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    business_name = models.CharField(max_length=100)
    secondary_contact = models.CharField(max_length=10, null=True, blank=True,
                                         validators=[MinLengthValidator(10), validate_phone])
    user_id = models.OneToOneField('MyUser', on_delete=models.CASCADE)


class Employee(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    entity_id = models.CharField(max_length=36)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    user_id = models.OneToOneField('MyUser', on_delete=models.CASCADE)


class EmployeeImage(models.Model):
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_employee_image,max_length=300, storage=get_storage())
