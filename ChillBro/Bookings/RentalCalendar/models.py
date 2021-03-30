from django.db import models


class RentBooking(models.Model):
    booking_id = models.CharField(max_length=16, verbose_name="Booking Id")
    product_id = models.CharField(max_length=16, verbose_name="Product Id")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        unique_together = (("booking_id", "product_id"),)

    def __str__(self):
        return "RentBooking Nº{0}".format(self.id)
