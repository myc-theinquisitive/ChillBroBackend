from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView, Response
from .models import ProductImage, Product, ProductSize
from .serializers import ProductImageSerializer, ProductQuantityUpdateSerializer
from ChillBro.permissions import IsBusinessClient, IsSellerProduct, IsSuperAdminOrMYCEmployee, IsOwnerById


class BaseProductImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self, request, *args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request, product_id)
        super().post(request, *args, **kwargs)


class BaseProductImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsSellerProduct)
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data['product']
        self.check_object_permissions(request, product_id)
        super().delete(request, *args, **kwargs)


class ProductQuantity(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsSellerProduct)

    def put(self, request, product_id):
        input_serializer = ProductQuantityUpdateSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't update product quantity",
                             "errors": input_serializer.errors}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(id=product_id)
        if len(products) != 1:
            return Response({"message": "Invalid Product id"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, product_id)

        size = request.data["size"]
        quantity = request.data["quantity"]

        if request.data["quantity"] <= 0:
            return Response({"message": "Can't update product quantity",
                             "errors": "Quantity should be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        # if product does not have size
        if not products[0].has_sizes:
            products.update(quantity=quantity)
            return Response({"message": "Updated Successfully"}, status=status.HTTP_200_OK)

        # if product has sizes
        if not size:
            return Response({"message": "Can't update product quantity",
                             "errors": "Product has sizes, Size should be specified"},
                            status=status.HTTP_400_BAD_REQUEST)

        product_sizes = ProductSize.objects.filter(product_id=product_id, size=size)
        if len(product_sizes) == 0:
            return Response({"message": "Can't update product quantity",
                             "errors": "Size for Product is not valid"},
                            status=status.HTTP_400_BAD_REQUEST)
        product_sizes.update(quantity=quantity)

        return Response({"message": "Updated Successfully"}, status=status.HTTP_200_OK)
