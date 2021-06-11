from django.db import models


class TravelPackageVehicle(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="travel_package_vehicle",
                                verbose_name="Vehicle")
    travel_package = models.ForeignKey("TravelPackage", on_delete=models.CASCADE, related_name="driver_for_vehicle",
                                       verbose_name="Default Driver")

    def __str__(self):
        return "Product: {0}".format(self.product.name)
