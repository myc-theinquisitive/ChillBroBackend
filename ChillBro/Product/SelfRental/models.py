from django.db import models


# TODO: price calculation per hour, per km details to be added??
class SelfRental(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")


    def __str__(self):
        return "Product: {0}".format(self.product.name)
