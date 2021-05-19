from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView, Response
from .models import ProductImage, Product
from .serializers import ProductImageSerializer, ProductQuantitySerializer
from ChillBro.permissions import IsBusinessClient, IsSellerProduct, IsSuperAdminOrMYCEmployee, IsOwnerById, \
    IsEmployeeBusinessClient


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


# TODO: should be updated to handle product with sizes
class ProductQuantity(APIView):
    serializer_class = ProductQuantitySerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | (IsBusinessClient & IsOwnerById) |
                          IsSellerProduct | IsEmployeeBusinessClient)

    def put(self, request, product_id):
        products = Product.objects.filter(id=product_id)
        if len(products) != 1:
            return Response({"message": "Invalid Product id"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, product_id)

        if request.data["quantity"] <= 0:
            return Response({"message": "Can't update product quantity",
                             "error": "Quantity should be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        products.update(quantity=request.data["quantity"])
        return Response({"message": "Updated Successfully"}, status=status.HTTP_200_OK)
