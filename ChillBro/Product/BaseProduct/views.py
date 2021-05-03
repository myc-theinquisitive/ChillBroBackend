from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer
from ..Seller.serializers import SellerProductSerializer
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta
from ..wrapper import get_booked_count_of_product_id
from ..constants import *
from ChillBro.permissions import IsBusinessClient, IsSellerProduct

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
    permission_classes = (IsAuthenticated, IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self,request,*args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request,product_id)
        super().post(request, *args, **kwargs)


class BaseProductImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def delete(self,request,*args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request,product_id)
        super().delete(request, *args, **kwargs)


class BusinessClientProductDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(id = kwargs['product_id'])
        except:
            return Response({"message":"invalid product id"},400)
        images = ProductImage.objects.filter(product_id=product).order_by('order')
        today_date = date.today()
        tomorrow_date = today_date + timedelta(1)
        total_booked = get_booked_count_of_product_id(kwargs['product_id'], today_date, tomorrow_date)
        all_images = []
        for each_image in images:
            all_images.append(each_image.image.url)
        discount = ((product.price - product.discounted_price)/product.price)*100
        product_details = {'product_id': product.id, 'name': product.name, 'description': product.description,
                "images": all_images, 'quantity': product.quantity, 'booked': total_booked, 'pricing': {
                "actual_price": product.price,
                "discount": discount,
                "discounted_price": product.discounted_price,
                "net_price": productNetPrice(product.price, discount)}}
        return Response(product_details,200)


def productNetPrice(selling_price, discount):
    final_selling_price = selling_price - (selling_price * discount) / 100
    commission_fee = final_selling_price * COMMISION_FEE_PERCENT / 100
    transaction_fee = final_selling_price * TRANSACTION_FEE_PERCENT / 100
    fixed_fee = final_selling_price * FIXED_FEE_PERCENT / 100
    gst = final_selling_price * GST_PERCENT / 100
    net_price = final_selling_price - (commission_fee + transaction_fee + fixed_fee + gst)
    return net_price


