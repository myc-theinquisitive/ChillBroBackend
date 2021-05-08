from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import *
from .helpers import *
from rest_framework.response import Response
from .wrapper import *
from django.db.models import Q
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClientEntities, \
    IsEmployeeEntities


class GetBookingTransactions(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BookingTransaction.objects.all()
    serializer_class = BookingTransactionDetailsSerializer


# TODO: Add api to get single transaction details based on ID


class UpdatePaymentDetailsFromMyc(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO: Add Image and amount for payment details and store the user who updated this
    #  Verify the total amount of bookings values is equal or not
    def put(self, request, *args, **kwargs):
        input_serializer = UpdateBookingTransactionSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        booking_ids = request.data["booking_ids"]
        pending_booking_ids = BookingTransaction.objects.filter(
            Q(paid_by__in=[PaymentUser.myc.value, PaymentUser.entity.value]),
            Q(paid_to__in=[PaymentUser.myc.value, PaymentUser.entity.value]),
            booking_id__in=booking_ids, payment_status=PayStatus.pending.value)\
            .values_list("booking_id", flat=True)

        invalid_booking_ids = set(booking_ids) - set(pending_booking_ids)
        if len(invalid_booking_ids) > 0:
            return Response({"message": "Unable to update transactions",
                             "error": "Invalid Booking ids {}".format(invalid_booking_ids)}, 400)

        BookingTransaction.objects.filter(
            Q(paid_by__in=[PaymentUser.myc.value, PaymentUser.entity.value]),
            Q(paid_to__in=[PaymentUser.myc.value, PaymentUser.entity.value]), booking_id__in=booking_ids)\
            .update(
                transaction_id=request.data["transaction_id"],
                utr=request.data["utr"],
                mode=request.data["mode"],
                transaction_date=request.data["transaction_date"],
                payment_status=PayStatus.done.value
            )
        return Response({"message": "Booking Transactions updated successfully"}, 200)


class CODBookingTransactionView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        input_serializer = CODBookingTransactionSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        booking_id = request.data["booking_id"]
        try:
            booking_transaction = BookingTransaction.objects.get(
                booking_id=booking_id, paid_by=PaymentUser.customer.value, paid_to=PaymentUser.entity.value)
        except ObjectDoesNotExist:
            return Response({"message": "Unable to update COD transaction",
                             "error": "Invalid Booking for COD"}, 400)

        if booking_transaction.payment_status != PayStatus.pending.value:
            return Response({"message": "Unable to update COD transaction",
                             "error": "COD transaction is not pending"}, 400)

        BookingTransaction.objects.filter(
            booking_id=booking_id, paid_by=PaymentUser.customer.value, paid_to=PaymentUser.entity.value)\
            .update(
                transaction_id=request.data["transaction_id"],
                utr=request.data["utr"],
                mode=request.data["mode"],
                transaction_date=request.data["transaction_date"],
                payment_status=PayStatus.done.value
            )
        return Response({"message": "COD Transaction updated successfully"}, 200)


class PaymentRevenueStatisticsView(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities, )

    # check entity id
    def get(self, request, *args, **kwargs):
        input_serializer = PaymentRevenueStatisticsViewSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        entity_id = request.data['entity_ids']
        date_filter = request.data['date_filter']
        entity_filter = getEntityType(request.data['entity_filters'])

        self.check_object_permissions(request, entity_id)

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        custom_generated_revenue = BookingTransaction.objects.generated_revenue_amount(
            from_date, to_date, entity_filter, entity_id)
        total_generated_revenue = BookingTransaction.objects.generated_revenue_amount(
            None, None, entity_filter, entity_id)

        custom_received_revenue = BookingTransaction.objects.received_revenue_amount(
            from_date, to_date, entity_filter, entity_id)
        total_received_revenue = BookingTransaction.objects.received_revenue_amount(
            None, None, entity_filter, entity_id)

        custom_pending_revenue = BookingTransaction.objects.pending_revenue_amount(
            from_date, to_date, entity_filter, entity_id)
        total_pending_revenue = BookingTransaction.objects.pending_revenue_amount(
            None, None, entity_filter, entity_id)

        custom_cancelled_revenue = BookingTransaction.objects.cancelled_revenue_amount(
            from_date, to_date, entity_filter, entity_id)
        total_cancelled_revenue = BookingTransaction.objects.cancelled_revenue_amount(
            None, None, entity_filter, entity_id)

        return Response(
            {
                "received_amount": {
                    "custom": custom_received_revenue,
                    "total": total_received_revenue
                },
                "generated_amount": {
                    "custom": custom_generated_revenue,
                    "total": total_generated_revenue
                },
                "pending_amount": {
                    "custom": custom_pending_revenue,
                    "total": total_pending_revenue
                },
                "cancelled_amount": {
                    "custom": custom_cancelled_revenue,
                    "total": total_cancelled_revenue
                }
            }, 200)


class GetPaymentsRevenueStatisticsDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = PaymentStatasticsDetailsInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filter = getEntityType(request.data['entity_filters'])
        entity_id = request.data['entity_ids']
        statistics_details_type = request.data['statistics_details_type']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from'], request.data['custom_dates']['to']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        transactions = []
        if statistics_details_type == "generated_revenue":
            transactions = BookingTransaction.objects.generated_revenue_transactions(
                from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == "received_revenue":
            transactions = BookingTransaction.objects.received_revenue_transactions(
                from_date, to_date, entity_filter, entity_id)
        if statistics_details_type == "pending_revenue":
            transactions = BookingTransaction.objects.pending_revenue_transactions(
                from_date, to_date, entity_filter, entity_id)
        if statistics_details_type == "cancelled_revenue":
            transactions = BookingTransaction.objects.cancelled_revenue_transactions(
                from_date, to_date, entity_filter, entity_id)

        transaction_serializer = BookingTransactionDetailsSerializer(transactions, many=True)
        return Response(transaction_serializer.data, 200)


# TODO: Create get api based on entity filters, entity ids, date filters - updated_at and payment status


class RefundTransactionList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionDetailsSerializer

    def post(self, request, *args, **kwargs):
        if "booking_id" not in request.data:
            return Response({"message": "Can't create refund transaction",
                             "error": "Booking Id should is present in Input"}, 400)

        booking_id = request.data["booking_id"]
        is_valid, booking_details = get_booking_details(booking_id)
        if not is_valid:
            return Response({"message": "Can't create refund transaction",
                             "error": "Invalid Booking Id"}, 400)

        request.data["entity_id"] = booking_details["entity_id"]
        request.data["entity_type"] = booking_details["entity_type"]
        request.data["booking_date"] = booking_details["booking_date"]
        request.data["booking_start"] = booking_details["booking_start"]

        request.data["initiated_by"] = request.user.id
        return super().post(request, args, kwargs)


class RefundTransactionDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = RefundTransaction.objects.all()
    serializer_class = RefundTransactionDetailsSerializer
