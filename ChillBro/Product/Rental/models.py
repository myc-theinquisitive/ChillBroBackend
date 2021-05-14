from django.db import models
from ..BaseProduct.models import Product


class RentalProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, verbose_name="Product")

    def __str__(self):
        return "Product: {0}".format(self.product.name)
