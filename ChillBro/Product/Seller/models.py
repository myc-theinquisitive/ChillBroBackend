from django.db import models


class SellerProduct(models.Model):
    seller_id = models.CharField(max_length=36)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Product Seller")

    class Meta:
        unique_together = ('product', 'seller_id',)

    def __str__(self):
        return "Seller - {0}, Product - {1}".format(self.seller_id, self.product_id)
