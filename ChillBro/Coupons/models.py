from django.db import models
from django.utils import timezone
from datetime import datetime

from .helpers import (get_random_code, get_coupon_code_length, get_user_model)


class Ruleset(models.Model):
    allowed_users = models.ForeignKey('AllowedUsersRule', on_delete=models.CASCADE, verbose_name="Allowed users rule")
    allowed_entities = models.ForeignKey('AllowedEntitiesRule', on_delete=models.CASCADE,
                                         verbose_name="Allowed entities rule")
    allowed_products = models.ForeignKey('AllowedProductsRule', on_delete=models.CASCADE,
                                         verbose_name="Allowed products rule")
    allowed_product_types = models.ForeignKey('AllowedProductTypesRule', on_delete=models.CASCADE,
                                              verbose_name="Allowed product types rule")
    max_uses = models.ForeignKey('MaxUsesRule', on_delete=models.CASCADE, verbose_name="Max uses rule")
    validity = models.ForeignKey('ValidityRule', on_delete=models.CASCADE, verbose_name="Validity rule")

    def __str__(self):
        return "Ruleset Nº{0}".format(self.id)

    class Meta:
        verbose_name = "Ruleset"
        verbose_name_plural = "Rulesets"


class AllowedEntitiesRule(models.Model):
    entities = models.TextField(verbose_name="Entities", blank=True, null=True)
    all_entities = models.BooleanField(default=True, verbose_name="All entities?")

    def __str__(self):
        if self.all_entities:
            return "AllowedEntitiesRule Nº{0} - ALL allowed".format(self.id)
        return "AllowedEntitiesRule Nº{0} - Specific allowed".format(self.id)

    class Meta:
        verbose_name = "Allowed Entities Rule"
        verbose_name_plural = "Allowed Entities Rules"


class AllowedUsersRule(models.Model):
    users = models.TextField(verbose_name="Users", blank=True, null=True)
    all_users = models.BooleanField(default=True, verbose_name="All users?")

    def __str__(self):
        if self.all_users:
            return "AllowedUsersRule Nº{0} - ALL allowed".format(self.id)
        return "AllowedUsersRule Nº{0} - Specific allowed".format(self.id)

    class Meta:
        verbose_name = "Allowed User Rule"
        verbose_name_plural = "Allowed User Rules"


class AllowedProductsRule(models.Model):
    products = models.TextField(verbose_name="Products", blank=True, null=True)
    all_products = models.BooleanField(default=True, verbose_name="All Products?")

    def __str__(self):
        if self.all_products:
            return "AllowedProductsRule Nº{0} - ALL allowed".format(self.id)
        return "AllowedProductsRule Nº{0} - Specific allowed".format(self.id)

    class Meta:
        verbose_name = "Allowed Product Rule"
        verbose_name_plural = "Allowed Product Rules"


class AllowedProductTypesRule(models.Model):
    product_types = models.TextField(verbose_name="Product Types", blank=True, null=True)
    all_product_types = models.BooleanField(default=True, verbose_name="All Product Types?")

    def __str__(self):
        if self.all_product_types:
            return "AllowedProductTypesRule Nº{0} - ALL allowed".format(self.id)
        return "AllowedProductTypesRule Nº{0} - Specific allowed".format(self.id)

    class Meta:
        verbose_name = "Allowed Product Type Rule"
        verbose_name_plural = "Allowed Product Type Rules"


class MaxUsesRule(models.Model):
    max_uses = models.BigIntegerField(default=0, verbose_name="Maximum uses")
    is_infinite = models.BooleanField(default=False, verbose_name="Infinite uses?")
    uses_per_user = models.IntegerField(default=1, verbose_name="Uses per User")

    def __str__(self):
        return "MaxUses-{0}, IsInfinite-{1}, UsesPerUser-{2}".format(self.max_uses, self.is_infinite, self.uses_per_user)

    class Meta:
        verbose_name = "Max Uses Rule"
        verbose_name_plural = "Max Uses Rules"


class ValidityRule(models.Model):
    start_date = models.DateTimeField(verbose_name="Start date", null=True)
    end_date = models.DateTimeField(verbose_name="End date", null=True)
    is_active = models.BooleanField(default=False, verbose_name="Is active?")
    minimum_order_value = models.IntegerField(default=0, verbose_name="Minimum Order value to avail the coupon")

    def __str__(self):
        return "IsActive-{0}, MinimumValue-{1}".format(self.is_active, self.minimum_order_value)

    class Meta:
        verbose_name = "Validity Rule"
        verbose_name_plural = "Validity Rules"


class CouponUserUsages(models.Model):
    coupon_user = models.ForeignKey('CouponUser', on_delete=models.CASCADE, verbose_name="Coupon User")
    coupon_usage = models.ForeignKey('CouponUsage', on_delete=models.CASCADE, verbose_name="Coupon Usage")

    def __str__(self):
        return "CouponUserUsages Nº{0}".format(self.id)


class CouponUsage(models.Model):
    coupon_user = models.ForeignKey('CouponUser', on_delete=models.CASCADE, verbose_name="Coupon User")
    order_id = models.TextField(max_length=36, verbose_name="Order id")
    discount_obtained = models.IntegerField(default=0, verbose_name="Discount Obtained")
    used_on = models.DateTimeField(default=timezone.now, verbose_name="Used on")

    def __str__(self):
        return "CouponUsage Nº{0}".format(self.id)


class CouponUser(models.Model):
    user_model = get_user_model()

    user = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="User")
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, verbose_name="Coupon")
    times_used = models.IntegerField(default=0, editable=False, verbose_name="Times used")
    coupon_usages = models.ManyToManyField(CouponUsage, through='CouponUserUsages')

    def __str__(self):
        return "CouponUser-{0}, TimesUsed-{1}".format(str(self.user), self.times_used)

    class Meta:
        verbose_name = "Coupon User"
        verbose_name_plural = "Coupon Users"


class Discount(models.Model):
    value = models.IntegerField(default=0, verbose_name="Value")
    is_percentage = models.BooleanField(default=False, verbose_name="Is percentage?")
    max_value_if_percentage = models.IntegerField(default=100, editable=is_percentage,
                                                  verbose_name="Max Discount (if percentage)")

    def __str__(self):
        if self.is_percentage:
            return "Discount-{0}%, MaximumDiscount-{1}Rs".format(self.value, self.max_value_if_percentage)

        return "Discount-{0}Rs".format(self.value)

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"


class Coupon(models.Model):
    code = models.CharField(max_length=get_coupon_code_length(), default=get_random_code,
                            verbose_name="Coupon Code", unique=True)
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    terms_and_conditions = models.TextField(null=True)
    discount = models.ForeignKey('Discount', on_delete=models.CASCADE)
    times_used = models.IntegerField(default=0, editable=False, verbose_name="Times used")
    created = models.DateTimeField(default=datetime.now, editable=False, verbose_name="Created")

    ruleset = models.ForeignKey('Ruleset', on_delete=models.CASCADE, verbose_name="Ruleset")

    def __str__(self):
        return "Code-{0}, TimesUsed-{1}".format(self.code, self.times_used)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Coupon, self).save(*args, **kwargs)


class CouponHistory(models.Model):
    user_model = get_user_model()
    code = models.CharField(max_length=get_coupon_code_length(), default=get_random_code,
                            verbose_name="Coupon Code")
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    terms_and_conditions = models.TextField(null=True)
    discount = models.ForeignKey('Discount', on_delete=models.CASCADE)
    times_used = models.IntegerField(default=0, editable=False, verbose_name="Times used")
    created = models.DateTimeField(default=datetime.now, editable=False, verbose_name="Created")

    ruleset = models.ForeignKey('Ruleset', on_delete=models.CASCADE, verbose_name="Ruleset")
    changed_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Changed By")

    def __str__(self):
        return "Code-{0}, ChangedBy-{1}".format(self.code, self.changed_by)
