from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import SellerProduct
from .serializers import SellerProductSerializer


class SellerProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer


class SellerProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer


class GetSellerProductList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer

    def get(self, request, *args, **kwargs):
        seller_id = kwargs["seller"]
        self.queryset = SellerProduct.objects.filter(seller_id=seller_id)
        return super().get(request, args, kwargs)
