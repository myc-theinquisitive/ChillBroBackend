from django.db import models


# TODO: price calculation per hour, per km details to be added??
class HireAVehicle(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="vehicle_product",
                                verbose_name="Vehicle")
    default_driver = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="driver_for_vehicle",
                                       verbose_name="Default Driver")

    def __str__(self):
        return "Product: {0}".format(self.product.name)
