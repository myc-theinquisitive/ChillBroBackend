import uuid

from django.db import models
from .validators import checkCouponId, checkProductId
from .constants import BookingStatus, PayStatus, EntityType, IdProofType, PayMode
from datetime import datetime
from .helpers import get_user_model, image_upload_to_user_id_proof


# Create your models here.
def getId():
    return str(uuid.uuid4())


class Bookings(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    coupon = models.CharField(max_length=36, validators=[checkCouponId], verbose_name="Coupon Id")
    booking_id = models.CharField(max_length=36, primary_key=True, default=getId, verbose_name="Booking Id")
    booking_date = models.DateTimeField(default=datetime.now)
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    entity_type = models.CharField(max_length=30,
                                   choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in
                                            EntityType], default=EntityType.hotels.value)
    booking_status = models.CharField(max_length=30,
                                      choices=[(booking_status.value, booking_status.value) for booking_status in
                                               BookingStatus],
                                      default=BookingStatus.pending.value)
    payment_status = models.CharField(max_length=30,
                                      choices=[(pay_status.value, pay_status.value) for pay_status in PayStatus],
                                      default=PayStatus.pending.value)
    entity_id = models.CharField(max_length=36)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return (self.booking_id)


class BookedProducts(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE, verbose_name="Booking Id")
    product_id = models.CharField(max_length=36, verbose_name="Product Id")
    quantity = models.IntegerField()
    product_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_cancelled = models.BooleanField(default=False)
    product_status = models.CharField(max_length=30,
                                      choices=[(product_status.value, product_status.value) for product_status in
                                               BookingStatus],
                                      default=BookingStatus.pending.value)

    class Meta:
        unique_together = (("booking_id", "product_id"),)

    def __str__(self):
        return "Ordered Product Nº{0}, Nº{1}".format(self.id, self.product_id)


class CheckInDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=datetime.now)
    is_caution_deposit_collected = models.BooleanField(default=False)
    caution_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    id_proof_type = models.CharField(max_length=30,
                                     choices=[(id_proof.value, id_proof.value) for id_proof in IdProofType],
                                     default=IdProofType.aadhar_card.value)
    id_image = models.ImageField(upload_to=image_upload_to_user_id_proof)

    def __str__(self):
        return str(self.booking_id)


class CheckOutDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    check_out = models.DateTimeField(default=datetime.now)
    caution_deposit_deductions = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    reason_for_deduction = models.CharField(max_length=10000, default='')
    rating = models.IntegerField(max_length=5, choices=[(rating, rating) for rating in range(1, 6)], default=5)
    review = models.CharField(max_length=10000, default='')

    def __str__(self):
        return str(self.booking_id)


class CancelledDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    cancelled_time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.booking_id)


class OtherImages(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    check_in = models.ForeignKey('CheckInDetails', on_delete=models.CASCADE)
    other_image_id = models.ImageField(upload_to=image_upload_to_user_id_proof)


class CheckOutProductImages(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    check_out = models.ForeignKey('CheckOutDetails', on_delete=models.CASCADE)
    product_image_id = models.ImageField(upload_to=image_upload_to_user_id_proof)


class TransactionDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50)
    utr = models.CharField(max_length=50)
    mode = models.CharField(max_length=10, choices=[(mode.value, mode.value) for mode in PayMode],
                            default=PayMode.upi.value)
    transaction_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.booking_id)


class BusinessClientReportOnCustomer(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    reasons_selected = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=10000)

    def __str__(self):
        return str(self.booking_id)
