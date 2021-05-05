from .models import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .constants import *
from .helpers import *
from .wrapper import *
from rest_framework.response import Response
from django.db.models import Sum, Q, FloatField, F
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntityById, IsEmployeeEntityById


# Create your views here.
class CreateBookingTransaction(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TransactionDetails.objects.all()
    serializer_class = TransactionDetailsSerializer


class GetPaymentsDetailsOfEachEntityView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntityById | IsEmployeeEntityById)

    # check entity id
    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['entity_id'])
        date_filter = request.data['date_filter']
        entity_filter = getEntityType(request.data['category_filters'])
        status = getStatus(request.data['status_filters'])
        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from'], request.data['custom_dates']['to']
        else:
            from_date, to_date = getTimePeriod(date_filter)
        transactions = TransactionDetails.objects.filter(entity_id=kwargs['entity_id'])
        entity_id = kwargs['entity_id']
        bookings = get_booking_details(entity_id, from_date, to_date, entity_filter, status)
        if len(bookings) == 0:
            return Response({"message": "invalid entity id or no bookings"}, 400)
        bookings_data = {}
        for each_booking in bookings:
            bookings_data[each_booking['booking_id']] = each_booking
        all_bookings = []
        for each_transaction in transactions:
            each_booking_list = {'booking_id': str(each_transaction.booking_id),
                                 'type': bookings_data[each_transaction.booking_id]['entity_type'],
                                 'transaction_id': each_transaction.transaction_id, 'utr': each_transaction.utr,
                                 'mode': each_transaction.mode,
                                 'transaction_made_on': each_transaction.transaction_date,
                                 'status': bookings_data[each_transaction.booking_id]['booking_status']
                                 }
            all_bookings.append(each_booking_list)
        all_details = {"Total Count": len(all_bookings), "results": all_bookings}
        return Response(all_details, 200)


class PaymentRevenueStatisticsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee |  IsBusinessClientEntityById | IsEmployeeEntityById)

    def get(self, request, *args, **kwargs):
        input_serializer = PaymentRevenueStatisticsViewSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filters'])
            entity_id = request.data['entity_ids']
            for id in entity_id:
                self.check_object_permissions(request, id)
            if date_filter == 'Total':
                total_revenue = TransactionDetails.objects \
                    .filter(Q(Q(entity_id__in=entity_id) & Q(entity_type__in=entity_filter))) \
                    .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))
                return Response(total_revenue['total_value'], 200)
            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            bookings_on_date_filter = TransactionDetails.objects \
                .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                          & Q(entity_id__in=entity_id) & Q(entity_type__in=entity_filter)))
            total_bookings = TransactionDetails.objects \
                .filter(Q(Q(entity_id__in=entity_id) & Q(entity_type__in=entity_filter)))
            received_amount_date_filter_value = bookings_on_date_filter \
                .filter(payment_status=PayStatus.done.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            pending_amount_date_filter_value = bookings_on_date_filter \
                .filter(payment_status=PayStatus.pending.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            total_received_amount_value = total_bookings \
                .filter(payment_status=PayStatus.done.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            total_pending_amount_value = total_bookings \
                .filter(payment_status=PayStatus.pending.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            if received_amount_date_filter_value['value'] is None:
                received_amount_date_filter_value['value'] = 0.0
            if pending_amount_date_filter_value['value'] is None:
                pending_amount_date_filter_value['value'] = 0.0
            if total_received_amount_value['value'] is None:
                total_received_amount_value['value'] = 0.0
            if total_pending_amount_value['value'] is None:
                total_pending_amount_value['value'] = 0.0
            return Response([{
                "recieved_amount": {
                    "today": received_amount_date_filter_value['value'] + pending_amount_date_filter_value['value'],
                    "total": total_received_amount_value['value'] + total_pending_amount_value['value']
                }}, {
                "generated_revenue": {
                    "today": received_amount_date_filter_value['value'],
                    "total": total_received_amount_value['value']
                }}, {
                "pending_amount": {
                    "today": pending_amount_date_filter_value['value'],
                    "total": total_pending_amount_value['value']
                }}], 200)
        else:
            return Response(input_serializer.errors, 400)
