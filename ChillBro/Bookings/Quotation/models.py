from django.db import models
import uuid


class BusinessClientQuotation(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    created_by = models.CharField(max_length=36)
    product = models.CharField(max_length=36)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    entity_id = models.CharField(max_length=36)
    quotation = models.ForeignKey('Quotation', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("created_by", "quotation")


class Quotation(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    booking_id = models.OneToOneField('Bookings',on_delete=models.CASCADE)
