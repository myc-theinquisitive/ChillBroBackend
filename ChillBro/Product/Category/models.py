from django.db import models
from .helpers import upload_image_to_category, update_image_to_category_icon


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE,
                                        null=True, verbose_name="Parent Category")
    icon_url = models.ImageField(upload_to=update_image_to_category_icon)

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

