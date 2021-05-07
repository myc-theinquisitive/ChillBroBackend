from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import SellerProduct
from .serializers import SellerProductSerializer
from ChillBro.permissions import IsBusinessClient


class SellerProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer


class SellerProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer

