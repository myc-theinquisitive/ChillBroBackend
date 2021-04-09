import django
from django.core.serializers import get_serializer
from django.db.models import Q
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import OrdersSerializer, OrderedProductSerializer
from .wrapper import get_total_products_value, get_coupons, get_individual_product_value
from Bookings.RentalCalendar.helpers import get_date_format
import time
from datetime import datetime, timedelta, date


# Create your views here.


class OrdersList(generics.ListCreateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    def post(self, request, *args, **kwargs):
        products_id_list = request.data.pop('products_id',None)
        request.data['total_money']=get_total_products_value(products_id_list)
        datetime_format = get_date_format()
        request.data['booking_date']=time.strftime(datetime_format)
        bookingsObject = OrdersSerializer()
        resultant = (bookingsObject.create(request.data))
        for i in products_id_list:
            i['booking_id']=resultant
            i['product_value']=get_individual_product_value(i['product_id'])
        orderedProductSerializerObject = OrderedProductSerializer()
        orderedProductSerializerObject.bulk_create(products_id_list)


class OrderedProductsList(generics.ListCreateAPIView):
    queryset = OrderedProducts.objects.all()
    serializer_class = OrderedProductSerializer
    def get(self, request, *args, **kwargs):
        order_id = request.data['order_id']
        orderedproducts = OrderedProducts.objects.filter(booking_id=order_id)
        response = django.core.serializers.serialize("json", orderedproducts)
        return HttpResponse(response, content_type='application/json')

class OrderDeleteList(generics.RetrieveUpdateDestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    lookup_field = 'pk'

class UserOrdersList(generics.ListCreateAPIView):
    user = get_user_id()
    queryset = Orders.objects.filter(user=user)
    serializer_class = OrdersSerializer

class CancelOrderList(generics.RetrieveUpdateAPIView):
    serializer_class = OrdersSerializer
    def put(self, request, *args, **kwargs):
        try:
            order = Orders.objects.get(booking_id=request.data['booking_id'])
        except:
            return Response({"error": "Order does'nt exist"})
        request.data['coupon'] = order.coupon
        request.data['booking_date'] = order.booking_date
        request.data['order_status'] = "CANCELLED"

        serializer = self.serializer_class(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class OrderDetailsListFilter(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):

        booking_filter = request.data['booking_filter']
        entity_filter = get_entity_type(request.data['entity_filter'])
        status = get_status(request.data['status'])
        from_date, to_date = get_time_period(booking_filter)
        print(from_date, to_date)
        if(from_date==None and to_date==None):
            return Response({"errors": "Invalid Date Filter!!!"}, 400)
        elif(entity_filter == None):
            return Response({"errors": "Invalid Entity Filter!!!"}, 400)
        else:
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date)& Q(booking_date__lte=to_date)\
                          & Q(entity_type__in=entity_filter) & Q(order_status__in=status)))
        serializer = OrdersSerializer(orders, many = True)
        return Response(serializer.data)


class StatisticsList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        booking_filter = request.data['booking_filter']
        entity_filter = get_entity_type(request.data['entity_filter'])
        status = get_status(request.data['status'])
        from_date, to_date = get_time_period(booking_filter)
        if (from_date == 0 and to_date == 0):
            return Response({"errors": "Invalid Date Filter!!!"}, 400)
        else:
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                          & Q(entity_type__in=entity_filter) & Q(order_status__in=status)))
        return HttpResponse(len(orders))



def get_entity_type(entity_filter):
    entities = ["Hotels", "Transport", "Rentals", "Resorts", "Events"]
    if entity_filter in entities:
        return entity_filter
    return entities


def get_time_period(booking_filter):
    datetime_format = "%Y-%m-%dT%H:%M:%S"
    datetime_format1 = "%Y-%m-%d"
    if (booking_filter == 'Today'):
        today = datetime.now()
        tomorrow = today + timedelta(1)
        return (today.strftime(datetime_format1),tomorrow.strftime(datetime_format1))
    elif (booking_filter == 'Yesterday'):
        today = datetime.now()
        yesterday = today - timedelta(1)
        return (yesterday.strftime(datetime_format1),today.strftime(datetime_format1))
    elif (booking_filter == 'Week'):
        today = datetime.now()
        week = today - timedelta(get_today_day())
        return (week.strftime(datetime_format),today.strftime(datetime_format))
    elif (booking_filter == 'Month'):
        today = datetime.now()
        month = today - timedelta(get_today_date())
        return (month.strftime(datetime_format),today.strftime(datetime_format))
    return (None,None)


def get_status(status):
    if len(status) == 0:
        return  ["PENDING", "ONGOING", "CANCELLED", "DONE"]
    return status

def get_today_day():
    now = datetime.now().strftime("%A")
    if now == "Sunday":
        return 0
    elif now == "Monday":
        return 1
    elif now == "Tuesday":
        return 2
    elif now == "Wednesday":
        return 3
    elif now == "Thursday":
        return 4
    elif now == "Friday":
        return 5
    elif now == "Saturday":
        return 6

def get_today_date():
    today = date.today().strftime("%d")
    return int(today)-1
















