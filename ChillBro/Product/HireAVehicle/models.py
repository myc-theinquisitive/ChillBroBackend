from django.db import models
from .constants import DurationType, TripType


# TODO: price calculation per hour, per km details to be added??
class HireAVehicle(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="vehicle_product",
                                verbose_name="Vehicle")
    default_driver = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="driver_for_vehicle",
                                       verbose_name="Default Driver")
    distance_price = models.ForeignKey("HireAVehicleDistancePrice", on_delete=models.CASCADE)
    duration_details = models.ForeignKey("HireAVehicleDurationDetails", on_delete=models.CASCADE)

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class HireAVehicleDistancePrice(models.Model):
    excess_km_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    km_hour_limit = models.PositiveIntegerField()
    km_day_limit = models.PositiveIntegerField()
    single_trip_return_value_per_km = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)


class HireAVehicleDurationDetails(models.Model):
    hour_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    day_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    excess_hour_duration_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    excess_day_duration_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)

    min_hour_duration = models.PositiveIntegerField(default=1)
    max_hour_duration = models.PositiveIntegerField(default=24)
    min_day_duration = models.PositiveIntegerField(default=1)
    max_day_duration = models.PositiveIntegerField(default=31)




