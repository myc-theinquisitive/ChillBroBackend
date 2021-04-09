import django
from django.db.models import Q
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from django.core import serializers
from .models import *
from .serializers import OrdersSerializer, OrderedProductSerializer
from .wrapper import get_total_products_value, get_coupons, get_individual_product_value
from Bookings.RentalCalendar.helpers import get_date_format
import time
from datetime import datetime, timedelta
# Create your views here.


class OrdersList(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)
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
            # print(i)
        orderedProductSerializerObject = OrderedProductSerializer()
        orderedProductSerializerObject.bulk_create(products_id_list)


class OrderedProductsList(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = OrderedProducts.objects.all()
    serializer_class = OrderedProductSerializer
    def get(self, request, *args, **kwargs):
        order_id = request.data['order_id']
        # print(order_id)
        orderedproducts = OrderedProducts.objects.filter(booking_id=order_id)
        response = django.core.serializers.serialize("json", orderedproducts)
        return HttpResponse(response, content_type='application/json')

class OrderDeleteList(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    lookup_field = 'pk'

class UserOrdersList(generics.ListCreateAPIView):
    #permission_classes = (IsAuthenticated,)
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
        request.data['order_status'] = 3
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
        if(entity_filter==0):
            return Response({"errors": "Entity Filter!!!"}, 400)
        from_date, to_date = get_time_period(booking_filter)
        if(from_date==0 and to_date==0):
            return Response({"errors": "Invalid Filter!!!"}, 400)
        if(entity_filter == "no" and status == "no"):
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date)))
        elif(entity_filter == "no"):
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date)& Q(booking_date__lte=to_date) & Q(order_status=status)))
        elif(status == "no"):
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date)& Q(booking_date__lte=to_date) & Q(entity_type=entity_filter)))
        else:
            orders = Orders.objects \
                .filter(Q(Q(booking_date__gte=from_date)& Q(booking_date__lte=to_date) & Q(entity_type=entity_filter) & Q(order_status=status)))
        if(request.data['count']==1):
            return HttpResponse(len(orders))
        response = django.core.serializers.serialize("json", orders)
        return HttpResponse(response, content_type='application/json')

def get_entity_type(entity_filter):
    if(len(entity_filter)==0):
        return "no"
    elif(entity_filter=="Hotels"):
        return 1
    elif(entity_filter == "Transport"):
        return 2
    elif(entity_filter == "Rentals"):
        return 3
    elif(entity_filter == "Resorts"):
        return 4
    elif(entity_filter == "Events"):
        return 5
    return 0


def get_time_period(booking_filter):
    datetime_format = "%Y-%m-%d"
    if (booking_filter == 'Today'):
        today = datetime.now()
        tomorrow = today + timedelta(1)
        return (today.strftime(datetime_format),tomorrow.strftime(datetime_format))
    elif (booking_filter == 'Yesterday'):
        today = datetime.now()
        yesterday = today - timedelta(1)
        return (yesterday.strftime(datetime_format),today.strftime(datetime_format))
    elif (booking_filter == 'Week'):
        today = datetime.now()
        week = today - timedelta(7)
        return (week.strftime(datetime_format),today.strftime(datetime_format))
    elif (booking_filter == 'Month'):
        today = datetime.now()
        month = today - timedelta(31)
        return (month.strftime(datetime_format),today.strftime(datetime_format))
    return (0,0)


def get_status(status):
    if (status == "PENDING"):
        return 1

    elif(status == "ONGOING"):
        return 2
    elif (status == "CANCELLED"):
        return 3
    elif (status == "DONE"):
        return 4
    else:
        return "no"


















