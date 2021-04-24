from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer
from ..Seller.serializers import SellerProductSerializer
from rest_framework.response import Response
from rest_framework import status

class BaseProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            product_id = serializer.data['id']
            request.data['product'] = product_id
            request.data['seller_id'] = request.user.id
            seller_product_serializer = SellerProductSerializer(data=request.data)
            if seller_product_serializer.is_valid():
                seller_product_serializer.save()
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            else:
                instance.delete()
                return Response(seller_product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'



class BaseProductImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class BaseProductImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

