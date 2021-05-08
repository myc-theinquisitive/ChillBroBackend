import uuid
from django.db.models import Q
from django.db import models
from .constants import BookingStatus, EntityType, IdProofType, ProductBookingStatus, PaymentStatus, PaymentMode
from datetime import datetime
from .helpers import get_user_model, image_upload_to_user_id_proof, image_upload_to_check_in, \
    image_upload_to_check_out


# Create your models here.
def get_id():
    return str(uuid.uuid4())


class BookingsManager(models.Manager):

    def active(self):
        return self.filter(~Q(payment_status=PaymentStatus.failed.value))

    def received_bookings(self, from_date, to_date, entity_types, entity_ids):
        if from_date and to_date:
            return self.active().filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date)
                                          & Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids)))
        elif from_date:
            return self.active().filter(Q(Q(booking_date__gte=from_date) & Q(entity_type__in=entity_types)
                                          & Q(entity_id__in=entity_ids)))
        elif to_date:
            return self.active().filter(Q(Q(booking_date__lte=to_date) & Q(entity_type__in=entity_types)
                                        & Q(entity_id__in=entity_ids)))
        else:
            return self.active().filter(Q(Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids)))

    def ongoing_bookings(self, entity_types, entity_ids):
        return self.active().filter(Q(Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids)) \
                                    & Q(booking_status=BookingStatus.ongoing.value))

    def pending_bookings(self, entity_types, entity_ids):
        return self.active().filter(Q(Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids)) \
                                    & Q(booking_status=BookingStatus.pending.value))

    def yet_to_take_bookings(self, from_date, to_date, entity_types, entity_ids):
        if to_date:
            return self.active().filter(Q(Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids))
                                        & Q(booking_status=BookingStatus.pending.value) & Q(start_time__lte=to_date))
        else:
            return self.active().filter(Q(Q(entity_type__in=entity_types) & Q(entity_id__in=entity_ids))
                                        & Q(booking_status=BookingStatus.pending.value))

    def yet_to_return_bookings(self, from_date, to_date, entity_filter, entity_ids):
        if to_date:
            return self.active().filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_ids))
                                        & Q(booking_status=BookingStatus.ongoing.value) & Q(end_time__lte=to_date))
        else:
            return self.active().filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_ids))
                                        & Q(booking_status=BookingStatus.ongoing.value))


class Bookings(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id, verbose_name="Booking Id")
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    coupon = models.CharField(max_length=36, null=True, blank=True, verbose_name="Coupon Id")
    booking_date = models.DateTimeField(default=datetime.now)
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    entity_type = models.CharField(
        max_length=30, choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in EntityType],
        default=EntityType.hotels.value)
    booking_status = models.CharField(
        max_length=30, choices=[(booking_status.value, booking_status.value) for booking_status in BookingStatus],
        default=BookingStatus.pending.value)
    payment_status = models.CharField(
        max_length=30, choices=[(pay_status.value, pay_status.value) for pay_status in PaymentStatus],
        default=PaymentStatus.pending.value)
    payment_mode = models.CharField(
        max_length=30, choices=[(pay_mode.value, pay_mode.value) for pay_mode in PaymentMode],
        default=PaymentMode.online.value)

    entity_id = models.CharField(max_length=36)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    objects = BookingsManager()

    def __str__(self):
        return self.id


class BookedProductManager(models.Manager):

    def active(self):
        return self.filter(~Q(booking__payment_status=PaymentStatus.failed.value))

    def total_bookings_for_product(self, product_id):
        return self.active().filter(product_id=product_id)

    def received_bookings_for_product(self, product_id, from_date, to_date):
        if from_date and to_date:
            return self.active().filter(product_id=product_id, booking__booking_date__gte=from_date,
                                        booking__booking_date__lte=to_date)
        elif from_date:
            return self.active().filter(product_id=product_id, booking__booking_date__gte=from_date)
        elif to_date:
            return self.active().filter(product_id=product_id, booking__booking_date__lte=to_date)
        else:
            return self.active().filter(product_id=product_id)

    def cancelled_bookings_for_product(self, product_id, from_date, to_date):
        if from_date and to_date:
            return self.active().filter(product_id=product_id, booking__booking_date__gte=from_date,
                                        booking__booking_date__lte=to_date,
                                        booking_status=ProductBookingStatus.cancelled.value)
        elif from_date:
            return self.active().filter(product_id=product_id, booking__booking_date__gte=from_date,
                                        booking_status=ProductBookingStatus.cancelled.value)
        elif to_date:
            return self.active().filter(product_id=product_id, booking__booking_date__lte=to_date,
                                        booking_status=ProductBookingStatus.cancelled.value)
        else:
            return self.active().filter(product_id=product_id, booking_status=ProductBookingStatus.cancelled.value)

    def ongoing_bookings_for_product(self, product_id):
        return self.active().filter(product_id=product_id, booking__booking_status=BookingStatus.ongoing.value)


class BookedProducts(models.Model):
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE, verbose_name="Booking")
    product_id = models.CharField(max_length=36, verbose_name="Product Id")
    quantity = models.IntegerField()
    product_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    net_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    booking_status = models.CharField(
        max_length=30, choices=[(booking_status.value, booking_status.value)
                                for booking_status in ProductBookingStatus],
        default=ProductBookingStatus.booked.value)

    objects = BookedProductManager()

    class Meta:
        unique_together = (("booking", "product_id"),)

    def __str__(self):
        return "Booked Product - {0}, {1}".format(self.booking_id, self.product_id)


class CheckInDetailsManager(models.Manager):

    def active(self):
        return self.filter(~Q(booking__payment_status=PaymentStatus.failed.value))

    def customer_taken(self, from_date, to_date, entity_types, entity_ids):
        if from_date and to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.ongoing.value)
                                        & Q(check_in__gt=from_date) & Q(check_in__lt=to_date)))
        elif from_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.ongoing.value)
                                        & Q(check_in__gt=from_date)))
        elif to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.ongoing.value)
                                        & Q(check_in__lt=to_date)))
        else:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.ongoing.value)))


class CheckInDetails(models.Model):
    booking = models.OneToOneField('Bookings', on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=datetime.now)
    is_caution_deposit_collected = models.BooleanField(default=False)
    caution_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    id_proof_type = models.CharField(
        max_length=30, choices=[(id_proof.value, id_proof.value) for id_proof in IdProofType],
        default=IdProofType.aadhar_card.value)
    id_image = models.ImageField(upload_to=image_upload_to_user_id_proof)

    objects = CheckInDetailsManager()

    def __str__(self):
        return self.booking_id


class CheckOutDetailsManager(models.Manager):

    def active(self):
        return self.filter(~Q(booking__payment_status=PaymentStatus.failed.value))

    def returned_bookings(self, from_date, to_date, entity_types, entity_ids):
        if from_date and to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.done.value)
                                        & Q(check_out__gt=from_date) & Q(check_out__lt=to_date)))
        elif from_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.done.value)
                                        & Q(check_out__gt=from_date)))
        elif to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.done.value)
                                        & Q(check_out__lt=to_date)))
        else:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_types) & Q(booking__entity_id__in=entity_ids)
                                        & Q(booking__booking_status=BookingStatus.done.value)))


class CheckOutDetails(models.Model):
    booking = models.OneToOneField('Bookings', on_delete=models.CASCADE)
    check_out = models.DateTimeField(default=datetime.now)
    caution_deposit_deductions = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    reason_for_deduction = models.CharField(max_length=10000, default='')

    objects = CheckOutDetailsManager()

    def __str__(self):
        return str(self.booking)


class CancelledDetailsManager(models.Manager):

    def active(self):
        return self.filter(~Q(booking__payment_status=PaymentStatus.failed.value))

    def cancelled_bookings(self, from_date, to_date, entity_filter, entity_id):
        if from_date and to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id)
                                        & Q(booking__booking_status=BookingStatus.cancelled.value)
                                        & Q(cancelled_time__gt=from_date) & Q(cancelled_time__lt=to_date)))
        elif from_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id)
                                        & Q(booking__booking_status=BookingStatus.cancelled.value)
                                        & Q(cancelled_time__gt=from_date)))
        elif to_date:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id)
                                        & Q(booking__booking_status=BookingStatus.cancelled.value)
                                        & Q(cancelled_time__lt=to_date)))
        else:
            return self.active().filter(Q(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id__in=entity_id)
                                        & Q(booking__booking_status=BookingStatus.cancelled.value)))


class CancelledDetails(models.Model):
    booking = models.OneToOneField('Bookings', on_delete=models.CASCADE)
    cancelled_time = models.DateTimeField(default=datetime.now)

    objects = CancelledDetailsManager()

    def __str__(self):
        return str(self.booking)


class CheckInImages(models.Model):
    check_in = models.ForeignKey('CheckInDetails', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_check_in)


class CheckOutImages(models.Model):
    check_out = models.ForeignKey('CheckOutDetails', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_check_out)


class BusinessClientReportOnCustomer(models.Model):
    booking = models.ForeignKey('Bookings', on_delete=models.CASCADE)
    reasons_selected = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=10000)

    def __str__(self):
        return str(self.booking)


class ReportCustomerReasons(models.Model):
    reason = models.CharField(max_length=100)

    def __str__(self):
        return "Reason - {0}".format(self.id)
