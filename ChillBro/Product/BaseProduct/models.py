from django.db import models
from .helpers import image_upload_to_product, get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from .constants import ProductTypes, ActivationStatus
from ..taggable_wrapper import get_taggable_manager, get_key_value_store
import uuid


def get_id():
    return str(uuid.uuid4())


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(activation_status=ActivationStatus.ACTIVE.value)

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


class Product(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    type = models.CharField(max_length=30, default=ProductTypes.Rental.value,
                            choices=[(product_type.value, product_type.value) for product_type in ProductTypes],
                            verbose_name="Product Type")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    discounted_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    featured = models.BooleanField(default=False)
    tags = get_taggable_manager()
    quantity = models.IntegerField(default=0)

    # For MYC verification
    active_from = models.DateTimeField(null=True, blank=True)
    activation_status = models.CharField(
        max_length=30, choices=[(status.name, status.value) for status in ActivationStatus],
        default=ActivationStatus.YET_TO_VERIFY.value)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    def get_slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name


class ProductVerification(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, verbose_name="Entity")
    comments = models.TextField(null=True, blank=True)
    user_model = get_user_model()
    verified_by = models.ForeignKey(user_model, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


kvstore = get_key_value_store()
kvstore.register(Product)


class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_product)
    order = models.IntegerField()

    class Meta:
        unique_together = ('product', 'order',)

    def __str__(self):
        return "Product Image - {0}".format(self.id)
