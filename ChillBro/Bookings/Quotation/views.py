from django.shortcuts import render
from rest_framework import generics

# Create your views here.
from .models import BusinessClientQuotation
from .serializers import BusinessClientQuotationSerializer


class BusinessClientQuotationList(generics.ListCreateAPIView):
    serializer_class = BusinessClientQuotationSerializer
    queryset = BusinessClientQuotation.objects.all()

    def get(self, request, *args, **kwargs):
        booking_id = request.data['booking_id']
        self.queryset = BusinessClientQuotation.objects.filter(booking_id=booking_id)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data['bc_id']=request.user.id
        return super().post(request, *args, **kwargs)


class BusinessClientQuotationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessClientQuotationSerializer
    queryset = BusinessClientQuotation.objects.all()

