from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import ProductImage
from .serializers import ProductImageSerializer
from ChillBro.permissions import IsBusinessClient, IsSellerProduct


class BaseProductImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self, request, *args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request, product_id)
        super().post(request, *args, **kwargs)


class BaseProductImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request, product_id)
        super().delete(request, *args, **kwargs)

