import uuid
from django.db.models import Q
from django.db import models
from .validators import checkCouponId, checkProductId
from .constants import BookingStatus, PayStatus, EntityType, IdProofType
from datetime import datetime, date, timedelta
from .helpers import get_user_model, image_upload_to_user_id_proof, image_upload_to_check_in, image_upload_to_check_out
from django.db.models import Count


# Create your models here.
def getId():
    return str(uuid.uuid4())


class BookingsManager(models.Manager):

    def received_bookings(self, from_date, to_date, entity_filter, entity_id):
        return self.filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                             & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)))

    def ongoing_bookings(self, entity_filter, entity_id):
        today_date = date.today() + timedelta(1)
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.ongoing.value))

    def pending_bookings(self, entity_filter, entity_id):
        today_date = date.today() + timedelta(1)
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.pending.value))

    def total_customer_yet_to_take_bookings(self, entity_filter, entity_id):
        today_date = date.today() + timedelta(1)
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.pending.value) & Q(start_time__lte=today_date))

    def customer_yet_to_take_bookings(self, from_date, to_date, entity_filter, entity_id):
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.pending.value) & Q(start_time__lte=to_date))

    def total_return_bookings(self, entity_filter, entity_id):
        today_date = date.today() + timedelta(1)
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.ongoing.value) & Q(end_time__lte=today_date))

    def yet_to_return_bookings(self, from_date, to_date, entity_filter, entity_id):
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.ongoing.value) & Q(end_time__lte=to_date))

    def total_received_bookings(self, entity_filter, entity_id):
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)))

    def total_cancelled_bookings(self, entity_filter, entity_id):
        return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)) \
                           & Q(booking_status=BookingStatus.cancelled.value))


class Bookings(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    coupon = models.CharField(max_length=36, verbose_name="Coupon Id")
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

    entity_id = models.CharField(max_length=36)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    objects = BookingsManager()

    def __str__(self):
        return (self.booking_id)


class BookedProducts(models.Model):
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE, verbose_name="Booking")
    product_id = models.CharField(max_length=36, verbose_name="Product Id")
    quantity = models.IntegerField()
    product_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_cancelled = models.BooleanField(default=False)
    product_status = models.CharField(max_length=30,
                                      choices=[(product_status.value, product_status.value) for product_status in
                                               BookingStatus],
                                      default=BookingStatus.pending.value)

    class Meta:
        unique_together = (("booking", "product_id"),)

    def __str__(self):
        return "Ordered Product Nº{0}, Nº{1}".format(self.id, self.product_id)


class CheckInDetailsManager(models.Manager):
    def customer_taken(self, from_date, to_date, entity_filter, entity_id):
        return self.select_related('booking') \
            .filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id) \
            & Q(booking__booking_status=BookingStatus.ongoing.value) \
            & Q(check_in__gt=from_date) & Q(check_in__lt=to_date)))

    def total_customer_taken_bookings(self, entity_filter, entity_id):
        return self.select_related('booking') \
            .filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id) \
            & Q(booking__booking_status=BookingStatus.ongoing.value)))


class CheckInDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=datetime.now)
    is_caution_deposit_collected = models.BooleanField(default=False)
    caution_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    id_proof_type = models.CharField(max_length=30,
                                     choices=[(id_proof.value, id_proof.value) for id_proof in IdProofType],
                                     default=IdProofType.aadhar_card.value)
    id_image = models.ImageField(upload_to=image_upload_to_user_id_proof)

    objects = CheckInDetailsManager()

    def __str__(self):
        return str(self.booking)

    class Meta:
        unique_together = ('booking','booking')


class CheckOutDetailsManager(models.Manager):
    def returned_bookings(self, from_date, to_date, entity_filter, entity_id):
        return self.select_related('booking') \
            .filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id) \
            & Q(booking__booking_status=BookingStatus.done.value) \
            & Q(check_out__gt=from_date) & Q(check_out__lt=to_date)))


class CheckOutDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    check_out = models.DateTimeField(default=datetime.now)
    caution_deposit_deductions = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    reason_for_deduction = models.CharField(max_length=10000, default='')

    objects = CheckOutDetailsManager()

    def __str__(self):
        return str(self.booking)

    class Meta:
        unique_together = ('booking','booking')


class CancelledDetailsManager(models.Manager):
    def cancelled_bookings(self, from_date, to_date, entity_filter, entity_id):
        return self.select_related('booking') \
                .filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id) \
                & Q(booking__booking_status=BookingStatus.cancelled.value)\
                & Q(cancelled_time__gt=from_date) & Q(cancelled_time__lt=to_date)))


class CancelledDetails(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    cancelled_time = models.DateTimeField(default=datetime.now)

    objects = CancelledDetailsManager()

    def __str__(self):
        return str(self.booking)

    class Meta:
        unique_together = ('booking','booking')


class CheckInImages(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    check_in = models.ForeignKey('CheckInDetails', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_check_in)


class CheckOutImages(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    check_out = models.ForeignKey('CheckOutDetails', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_check_out)


class BusinessClientReportOnCustomer(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=getId)
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    reasons_selected = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=10000)

    def __str__(self):
        return str(self.booking)


class ReportCustomerResons(models.Model):
    reason = models.CharField(max_length=1000)

    def __str__(self):
        return "Reason - {0}".format(self.id)