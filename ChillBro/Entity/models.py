from django.db import models
from django.db.models import Q

from .constants import Status, EntityType, BankAccountTypes, ActivationStatus, EntitySubType
import uuid
from django.core.validators import MinLengthValidator
from .helpers import get_user_model, image_upload_to_amenities, upload_image_for_entity
from .validations import validate_pan, validate_aadhar, validate_registration, validate_gst, \
    validate_bank_account_no, validate_ifsc_code, validate_upi_id, validate_phone
from .helpers import upload_aadhar_image_for_entity, upload_gst_image_for_entity, upload_pan_image_for_entity, \
    upload_registration_image_for_entity


class Amenities(models.Model):
    name = models.CharField(max_length=40)
    icon_url = models.ImageField(upload_to=image_upload_to_amenities)

    def __str__(self):
        return self.name


class EntityManager(models.Manager):
    def active(self):
        return self.filter(activation_status=ActivationStatus.ACTIVE.value)

    def search(self, query):
        lookups = (Q(name__icontains=query))
        return self.filter(lookups).distinct()


class MyEntity(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    name = models.CharField(max_length=100, verbose_name="Name")
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=30, choices=[(etype.name, etype.value) for etype in EntityType])
    sub_type = models.CharField(
        max_length=30, choices=[(esubtype.name, esubtype.value) for esubtype in EntitySubType], null=True, blank=True)

    status = models.CharField(
        max_length=30, choices=[(status.name, status.value) for status in Status], default=Status.OFFLINE.value)
    address_id = models.CharField(max_length=36)

    registration = models.OneToOneField('EntityRegistration', on_delete=models.CASCADE)
    account = models.OneToOneField('EntityAccount', on_delete=models.CASCADE)
    upi = models.OneToOneField('EntityUPI', on_delete=models.CASCADE)

    # For MYC verification
    active_from = models.DateTimeField(null=True, blank=True)
    activation_status = models.CharField(
        max_length=30, choices=[(status.name, status.value) for status in ActivationStatus],
        default=ActivationStatus.YET_TO_VERIFY.value)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EntityManager()

    def __str__(self):
        return self.name + '-' + self.activation_status

    class Meta:
        ordering = ['-created_at']


class EntityImage(models.Model):
    entity = models.ForeignKey("MyEntity", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_for_entity)
    order = models.IntegerField()

    class Meta:
        unique_together = ('entity', 'order',)
        ordering = ['order']

    def __str__(self):
        return "Entity Image - {0}".format(self.id)


class EntityAvailableAmenities(models.Model):
    entity = models.ForeignKey('MyEntity', on_delete=models.CASCADE, verbose_name="Entity")
    amenity = models.ForeignKey("Amenities", on_delete=models.CASCADE, verbose_name="Amenities")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('entity', 'amenity',)

    def __str__(self):
        return "Entity: {0}, Amenities: {1}, Is Available {2}"\
            .format(self.entity_id, self.amenity.name, self.is_available)


class EntityRegistration(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)

    pan_no = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_pan])
    registration_no = models.CharField(max_length=21, validators=[MinLengthValidator(21), validate_registration])
    gst_in = models.CharField(max_length=15, validators=[MinLengthValidator(15), validate_gst])
    aadhar_no = models.CharField(max_length=14, validators=[MinLengthValidator(14), validate_aadhar])

    pan_image = models.ImageField(upload_to=upload_pan_image_for_entity, max_length=500)
    registration_image = models.ImageField(upload_to=upload_registration_image_for_entity, max_length=500)
    gst_image = models.ImageField(upload_to=upload_gst_image_for_entity, max_length=500)
    aadhar_image = models.ImageField(upload_to=upload_aadhar_image_for_entity, max_length=500)


class EntityAccount(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    bank_name = models.CharField(max_length=60)
    account_no = models.CharField(max_length=18, validators=[MinLengthValidator(9), validate_bank_account_no])
    ifsc_code = models.CharField(max_length=11, validators=[MinLengthValidator(11), validate_ifsc_code])
    account_type = models.CharField(max_length=20, choices=[(type.name, type.value) for type in BankAccountTypes])
    account_holder_name = models.CharField(max_length=60)


class EntityUPI(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    upi_id = models.CharField(max_length=100, validators=[MinLengthValidator(5), validate_upi_id])
    phone_pe = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])
    g_pay = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])
    pay_tm = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])


class EntityVerification(models.Model):
    entity = models.OneToOneField('MyEntity', on_delete=models.CASCADE, verbose_name="Entity")
    comments = models.TextField(null=True, blank=True)
    user_model = get_user_model()
    verified_by = models.ForeignKey(user_model, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class BusinessClientEntity(models.Model):
    entity = models.ForeignKey('MyEntity', on_delete=models.CASCADE, verbose_name="Booking")
    user_model = get_user_model()
    business_client = models.ForeignKey(user_model, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("entity", "business_client"),)

    def __str__(self):
        return 'business client: ' + self.business_client_id + ' - entity: ' + self.entity_id
