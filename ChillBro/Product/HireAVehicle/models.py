from django.db import models
from .constants import DurationType, TripType


# TODO: price calculation per hour, per km details to be added??
class HireAVehicle(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="vehicle_product",
                                verbose_name="Vehicle")
    default_driver = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="driver_for_vehicle",
                                       verbose_name="Default Driver")

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class HireAVehicleDistancePrice(models.Model):
    duration_type = models.CharField(max_length=30, \
                        choices=[(duration_type.value, duration_type.value) for duration_type in DurationType], \
                        default = DurationType.hour.value)
    km_limit = models.PositiveIntegerField()
    km_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    excess_km_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    excess_duration_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_infinity = models.BooleanField(default=False)
    single_trip_return_value_per_km = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    min_time_duration = models.PositiveIntegerField(default=1)
    max_time_duration = models.PositiveIntegerField(default=30)
    hire_a_vehicle = models.ForeignKey('HireAVehicle', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('hire_a_vehicle', 'duration_type')


