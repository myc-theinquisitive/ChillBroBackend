from django.db import models
from .helpers import image_upload_to_product
from django.db.models import Q
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from .constants import ProductTypes, ProductStatus
import string
import random
from django.core.exceptions import ValidationError
from ..wrapper import get_taggable_manager, get_key_value_store


def validate_product_type(value):
    product_values = [product_type.value for product_type in ProductTypes]
    if value in product_values:
        return value
    else:
        raise ValidationError("Invalid Product Type!")


def get_random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(name__icontains=query) |
                   Q(description__icontains=query) |
                   Q(tags__name__icontains=query)
                   )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(TimeStampModel):
    name = models.CharField(max_length=120)
    slug= models.SlugField(blank=True)
    description = models.TextField()
    type = models.CharField(max_length=30, default=ProductTypes.Rental.value,
                            choices=[(product_type.value, product_type.value) for product_type in ProductTypes],
                            verbose_name="Product Type", validators=[validate_product_type])
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    discounted_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    tags = get_taggable_manager()
    status = models.CharField(max_length=20,choices=[(product_status.value, product_status.value) for product_status in ProductStatus], default=ProductStatus.PENDING.value)
    quantity = models.IntegerField()
    objects = ProductManager()

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    def get_slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name


kvstore = get_key_value_store()
kvstore.register(Product)


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.slug = instance.get_slug()


pre_save.connect(product_pre_save_receiver, sender=Product)


class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_product)
    order = models.IntegerField()

    class Meta:
        unique_together = ('product', 'order',)

    def __str__(self):
        return "Product Image - {0}".format(self.id)

