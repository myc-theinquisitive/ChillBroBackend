from django.db import models
import uuid


def get_id():
    return str(uuid.uuid4())


class PaidAmenities(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")

    def __str__(self):
        return "Product: {0}".format(self.product.name)

