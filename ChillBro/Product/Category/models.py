from django.db import models
from .helpers import image_upload_to_category, iconUrlImage


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE,
                                        blank=True, null=True, verbose_name="Parent Category")
    icon_url = models.ImageField(upload_to=iconUrlImage)

    def __str__(self):
        return "Category - Nº{0}".format(self.name)


class CategoryImage(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_category)
    order = models.IntegerField()

    class Meta:
        unique_together = ('category', 'order',)

    def __str__(self):
        return "Category Image - Nº{0}".format(self.id)

