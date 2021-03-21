from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer


class BaseProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BaseProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class BaseProductImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
