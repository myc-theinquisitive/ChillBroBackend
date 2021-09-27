from django.db import models
from .validations import is_json
from .constants import EventMode, EventHostApp, EventPaymentType


class Events(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")

    mode = models.CharField(max_length=30, default=EventMode.offline.value,
                            choices=[(mode.value, mode.value) for mode in EventMode],
                            verbose_name="Event Mode")
    host_app = models.CharField(max_length=30, null=True, blank=True,
                                choices=[(host_app.value, host_app.value) for host_app in EventHostApp],
                                verbose_name="Event Mode")
    url_link = models.CharField(max_length=300, null=True, blank=True)

    payment_type = models.CharField(max_length=30, default=EventPaymentType.paid.value,
                                    choices=[(payment_type.value, payment_type.value)
                                             for payment_type in EventPaymentType],
                                    verbose_name="Event Payment Type")
    # If there are no slots them only one slot for entire event so consider event duration
    has_slots = models.BooleanField(default=False, verbose_name="Has Slots?")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    tags = models.TextField(validators=[is_json])

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class EventSlots(models.Model):
    event = models.ForeignKey("Events", on_delete=models.CASCADE, verbose_name="Event")
    name = models.CharField(max_length=50)
    day_start_time = models.TimeField()
    day_end_time = models.TimeField()

    class Meta:
        unique_together = ('event', 'name',)

    def __str__(self):
        return "Event Slot: {0}: {1} - {2}".format(self.name, self.day_start_time, self.day_end_time)


class EventPriceClasses(models.Model):
    event = models.ForeignKey("Events", on_delete=models.CASCADE, verbose_name="Event")
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)

    class Meta:
        unique_together = ('event', 'name',)

    def __str__(self):
        return "Event Price Classes: {0}: {1}".format(self.name, self.price)
