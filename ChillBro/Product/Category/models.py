from django.db import models
from .helpers import upload_image_to_category, update_image_to_category_icon
import uuid


def get_id():
    return str(uuid.uuid4())


class Category(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE,
                                        null=True, verbose_name="Parent Category")
    icon_url = models.ImageField(upload_to=update_image_to_category_icon,max_length = 300)

    def __str__(self):
        return "Category - Nº{0}".format(self.name)


class CategoryImage(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_to_category)
    order = models.IntegerField()

    class Meta:
        unique_together = ('category', 'order',)

    def __str__(self):
        return "Category Image - Nº{0}".format(self.id)


class CategoryPrices(models.Model):
    category = models.OneToOneField("Category", on_delete=models.CASCADE)
    min_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    max_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    min_discount = models.IntegerField(default=0)
    max_discount = models.IntegerField(default=0)

