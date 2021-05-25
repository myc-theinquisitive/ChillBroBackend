from django.db import models
import uuid
from django.db.models import Q, Sum, F, FloatField
from .constants import PayMode, PayStatus, EntityType, PaymentUser
from .helpers import get_user_model, image_upload_to_transaction_proof


def get_id():
    return str(uuid.uuid4())


class BookingTransactionsManager(models.Manager):

    def entity_transaction_filters(self, from_date, to_date, entity_filter, entity_id):
        if from_date and to_date:
            return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id) &
                                 Q(booking_date__gt=from_date) & Q(booking_date__lt=to_date)))
        elif from_date:
            return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id) &
                                 Q(booking_date__gt=from_date)))
        elif to_date:
            return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id) &
                                 Q(booking_date__lt=to_date)))
        else:
            return self.filter(Q(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)))

    def generated_revenue_transactions(self, from_date, to_date, entity_filter, entity_id):
        return self.entity_transaction_filters(from_date, to_date, entity_filter, entity_id)\
            .filter(~Q(payment_status=PayStatus.cancelled.value))

    def pending_revenue_transactions(self, from_date, to_date, entity_filter, entity_id):
        return self.entity_transaction_filters(from_date, to_date, entity_filter, entity_id)\
            .filter(payment_status=PayStatus.pending.value)

    def received_revenue_transactions(self, from_date, to_date, entity_filter, entity_id):
        return self.entity_transaction_filters(from_date, to_date, entity_filter, entity_id)\
            .filter(payment_status=PayStatus.done.value)

    def cancelled_revenue_transactions(self, from_date, to_date, entity_filter, entity_id):
        return self.entity_transaction_filters(from_date, to_date, entity_filter, entity_id)\
            .filter(payment_status=PayStatus.cancelled.value)

    def generated_revenue_amount(self, from_date, to_date, entity_filter, entity_id):
        entity_amount = self.generated_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.entity.value)\
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if entity_amount is None:
            entity_amount = 0
        myc_amount = self.generated_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.myc.value) \
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if myc_amount is None:
            myc_amount = 0
        return entity_amount - myc_amount

    def pending_revenue_amount(self, from_date, to_date, entity_filter, entity_id):
        entity_amount = self.pending_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.entity.value)\
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if entity_amount is None:
            entity_amount = 0
        myc_amount = self.pending_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.myc.value) \
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if myc_amount is None:
            myc_amount = 0
        return entity_amount - myc_amount

    def received_revenue_amount(self, from_date, to_date, entity_filter, entity_id):
        entity_amount = self.received_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.entity.value)\
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if entity_amount is None:
            entity_amount = 0
        myc_amount = self.received_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.myc.value) \
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if myc_amount is None:
            myc_amount = 0
        return entity_amount - myc_amount

    def cancelled_revenue_amount(self, from_date, to_date, entity_filter, entity_id):
        entity_amount = self.cancelled_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.entity.value)\
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if entity_amount is None:
            entity_amount = 0
        myc_amount = self.cancelled_revenue_transactions(from_date, to_date, entity_filter, entity_id)\
            .filter(paid_to=PaymentUser.myc.value) \
            .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))['total_value']
        if myc_amount is None:
            myc_amount = 0
        return entity_amount - myc_amount


class BookingTransaction(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)

    # booking details
    booking_id = models.CharField(max_length=36)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=30, choices=[(type_of_entity.value, type_of_entity.value)
                                                           for type_of_entity in EntityType])
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    booking_date = models.DateTimeField()
    booking_start = models.DateTimeField()

    # Payment details
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    utr = models.CharField(max_length=50, blank=True, null=True)
    mode = models.CharField(max_length=10, choices=[(mode.value, mode.value) for mode in PayMode],
                            default=PayMode.not_done.value)
    transaction_date = models.DateTimeField(null=True, blank=True)

    payment_status = models.CharField(max_length=30,
                                      choices=[(pay_status.value, pay_status.value) for pay_status in PayStatus],
                                      default=PayStatus.pending.value)
    paid_to = models.CharField(max_length=30, choices=[(pay_user.value, pay_user.value) for pay_user in PaymentUser],
                               default=PaymentUser.entity.value)
    paid_by = models.CharField(max_length=30, choices=[(pay_user.value, pay_user.value) for pay_user in PaymentUser],
                               default=PaymentUser.myc.value)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_proof = models.ImageField(upload_to=image_upload_to_transaction_proof, blank=True, null=True)
    credited_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, blank=True, null=True)

    objects = BookingTransactionsManager()

    class Meta:
        unique_together = (("booking_id", "paid_to", "paid_by"),)
        ordering = ["-created_at"]

    def __str__(self):
        return self.id + " Booking: " + self.booking_id


class RefundTransaction(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)

    # booking details
    booking_id = models.CharField(max_length=36)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=30, choices=[(type_of_entity.value, type_of_entity.value)
                                                           for type_of_entity in EntityType])
    booking_date = models.DateTimeField()
    booking_start = models.DateTimeField()

    # refund details
    refund_amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    user_model = get_user_model()
    initiated_by = models.ForeignKey(user_model, on_delete=models.CASCADE, null=True, blank=True)
    bank_details = models.TextField(null=True, blank=True)
    refund_reason = models.TextField()

    payment_status = models.CharField(max_length=30,
                                      choices=[(pay_status.value, pay_status.value) for pay_status in PayStatus],
                                      default=PayStatus.pending.value)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    utr = models.CharField(max_length=50, blank=True, null=True)
    mode = models.CharField(max_length=10, choices=[(mode.value, mode.value) for mode in PayMode],
                            default=PayMode.not_done.value)
    transaction_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.id + " Booking: " + self.booking_id
