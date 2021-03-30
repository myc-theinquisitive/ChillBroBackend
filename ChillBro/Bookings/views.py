import django
from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .validators import getUserId
from django.core import serializers

from .models import *
from .serializers import *
# Create your views here.


class OrdersList(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer


class OrderedProductsList(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)
    # queryset = OrderedProducts.objects.all()
    # serializer_class = OrderedProductSerializer
    def get(self, request, *args, **kwargs):
        order_id = request.data['order_id']
        print(order_id)
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
    user = getUserId()
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

class OrderDetailsList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        from_date = request.data['from_date']
        to_date = request.data['to_date']
        orders = Orders.objects.filter(Q(Q(booking_date__gte=from_date)& Q(booking_date__lte=to_date)))
        response = django.core.serializers.serialize("json", orders)
        return HttpResponse(response, content_type='application/json')

















