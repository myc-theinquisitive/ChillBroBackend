from django.shortcuts import render
from rest_framework import generics

# Create your views here.
from .models import BusinessClientQuotation, Quotation
from .serializers import BusinessClientQuotationSerializer
from rest_framework.response import Response


class BusinessClientQuotationList(generics.ListCreateAPIView):
    serializer_class = BusinessClientQuotationSerializer
    queryset = BusinessClientQuotation.objects.all()

    def get(self, request, *args, **kwargs):
        booking_id = request.data['booking_id']
        try:
            quotation = Quotation.objects.get(booking_id=booking_id)
        except:
            return Response({"message": "No quotations found", "error": "invalid booking id"})
        self.queryset = BusinessClientQuotation.objects.filter(quotation_id=quotation.id)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data['created_by'] = request.user.id
        return super().post(request, *args, **kwargs)


class BusinessClientQuotationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessClientQuotationSerializer
    queryset = BusinessClientQuotation.objects.all()
