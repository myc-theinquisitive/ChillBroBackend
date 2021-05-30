from django.db import models
from .helpers import image_upload_to_product, get_user_model
from django.db.models import Q
from .constants import ProductTypes, ActivationStatus, PriceTypes
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
    description = models.TextField()

    type = models.CharField(max_length=30, default=ProductTypes.Rental.value,
                            choices=[(product_type.value, product_type.value) for product_type in ProductTypes],
                            verbose_name="Product Type")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    seller_id = models.CharField(max_length=36)

    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    discounted_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    price_type = models.CharField(max_length=30, default=PriceTypes.DAY.value,
                                  choices=[(price_type.value, price_type.value) for price_type in PriceTypes],
                                  verbose_name="Price Type")

    featured = models.BooleanField(default=False)
    tags = get_taggable_manager()
    has_sizes = models.BooleanField(default=False)

    # if there are no sizes use this quantity field else check quantity from the product size model
    quantity = models.PositiveIntegerField(default=0)

    # For combo products
    is_combo = models.BooleanField(default=False)

    # For MYC verification
    active_from = models.DateTimeField(null=True, blank=True)
    activation_status = models.CharField(
        max_length=30, choices=[(status.name, status.value) for status in ActivationStatus],
        default=ActivationStatus.YET_TO_VERIFY.value)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Product")
    size = models.CharField(max_length=10, verbose_name="Size")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity")
    order = models.PositiveIntegerField(verbose_name="Order")

    class Meta:
        unique_together = (('product', 'size'), ('product', 'order'), )
        ordering = ('order', )

    def __str__(self):
        return "Product Size - {0}, {1}, {2}".format(self.product.id, self.size, self.quantity)


class ComboProductItems(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    combo_item = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Combo Item",
                                   related_name="combo_item")

    class Meta:
        unique_together = ('product', 'combo_item',)
        ordering = ['id']

    def __str__(self):
        return "Combo item - {0}, {1}".format(self.product.id, self.combo_item.id)


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
        ordering = ['order']

    def __str__(self):
        return "Product Image - {0}".format(self.id)
