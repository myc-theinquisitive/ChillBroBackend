from django.core.validators import MinLengthValidator
from django.db import models
from authentication.models import EmailUserManager, EmailAbstractUser
from .validations import validate_phone


class MyUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField('Date of birth', null=True, blank=True)
    phone_number=models.CharField('phone_number',max_length=10,unique=True,null=True,blank=True,validators=[MinLengthValidator(10),validate_phone])


    # Required
    objects = EmailUserManager()

