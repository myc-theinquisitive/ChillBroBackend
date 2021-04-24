from .models import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .constants import *
from datetime import date, timedelta
from .helpers import *
from .wrapper import *
from rest_framework.response import Response
from django.db.models import Sum, Q, FloatField, F


# Create your views here.
def getEntityType(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities

def getStatus(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status

def getTimePeriod(date_filter):
    if date_filter == 'Today':
        today = date.today()
        tomorrow = today + timedelta(1)
        return today, tomorrow
    elif date_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        return week, today + timedelta(1)
    elif date_filter == 'Month':
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, today + timedelta(1)
    return None, None


class CreateBookingTransaction(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TransactionDetails.objects.all()
    serializer_class = TransactionDetailsSerializer


class GetPaymentsDetailsOfEachEntityView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        date_filter = request.data['date_filter']
        entity_filter = getEntityType(request.data['category_filters'])
        status = getStatus(request.data['status_filters'])
        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from'], request.data['custom_dates']['to']
        else:
            from_date, to_date = getTimePeriod(date_filter)
        transactions = TransactionDetails.objects.all()
        entity_id = kwargs['entity_id']
        bookings = getBookingDetails(entity_id, from_date, to_date, entity_filter, status)
        if len(bookings) == 0:
            return Response({"message": "invalid entity id or no bookings"}, 400)
        bookings_data ={}
        for each_booking in bookings:
            bookings_data[each_booking.booking_id] = each_booking
        all_bookings = []
        for each_transaction in transactions:
            each_booking_list = {'booking_id': str(each_transaction.booking_id),
                                 'type': bookings_data[each_transaction.booking_id].entity_type,
                                 'transaction_id': each_transaction.transaction_id, 'utr': each_transaction.utr,
                                 'mode': each_transaction.mode,
                                 'transaction_made_on': each_transaction.transaction_date,
                                 'status': bookings_data[each_transaction.booking_id].booking_status
                                 }
            all_bookings.append(each_booking_list)
        all_details = {"Total Count": len(all_bookings), "results": all_bookings}
        return Response(all_details, 200)


class PaymentRevenueStatisticsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = PaymentRevenueStatisticsViewSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filters'])
            entity_id = request.data['entity_ids']
            if date_filter == 'Total':
                total_revenue = getBookingDetailsByEntityIdByEntityType(entity_filter, entity_id)\
                        .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))
                return Response(total_revenue['total_value'], 200)
            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            bookings_on_date_filter = getBookingDetailsByDateByEntityIdByEntityType(from_date, to_date, entity_filter, entity_id)
            total_bookings = getBookingDetailsByEntityIdByEntityType(entity_filter, entity_id)
            received_amount_date_filter_value = bookings_on_date_filter \
                .filter(payment_status = PayStatus.done.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            pending_amount_date_filter_value = bookings_on_date_filter \
                .filter(payment_status = PayStatus.pending.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            total_received_amount_value = total_bookings \
                .filter(payment_status = PayStatus.done.value) \
                .aggregate(value=Sum(F('total_money'), output_field=FloatField()))
            total_pending_amount_value = total_bookings \
                .filter(payment_status = PayStatus.pending.value) \
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