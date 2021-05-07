from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .wrapper import check_valid_booking, get_product_details_with_image, check_valid_product
from .helpers import get_date_format
from collections import defaultdict
# Create your views here.


class AddProductToCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToCartSerializer(data=request.data)
        if input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)

        entity_id, entity_type = check_valid_product(request.data['product_id'])
        if entity_id is None and entity_type is None:
            return Response({"message": "Can't add product to cart", "errors": "Invalid Product"})

        is_valid, errors = check_valid_booking(request.data['product_id'], request.data['quantity'],
                                               request.data['start_time'], request.data['end_time'])
        if not is_valid:
            return Response({"message": "Can't add product to cart", "errors": errors}, 400)

        try:
            cart = Cart.objects.get(entity_id=entity_id, entity_type=entity_type, start_time=request.data['start_time'],
                                    end_time=request.data['end_time'], created_by=request.user)
        except ObjectDoesNotExist:
            serializer = CartSerializer()
            cart = serializer.create(
                {
                    'entity_id': entity_id,
                    'entity_type': entity_type,
                    'start_time': request.data['start_time'],
                    'end_time': request.data['end_time'],
                    'created_by': request.user
                }
            )
        cart_product_serializer = CartProductsSerializer()
        cart_product_serializer.create(
            {
                "cart": cart,
                "product_id": request.data['product_id'],
                "quantity": request.data['quantity']
            }
        )
        return Response({"message": "Product added to cart successfully", "cart_id": cart.id}, 200)


class UpdateCartProductQuantity(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        cart_products = CartProducts.objects.select_related('cart').filter(
            cart=request.data['cart'], product_id=request.data['product_id'])
        if len(cart_products) == 0:
            return Response({"message": "Can't update the product quantity",
                             "errors": "invalid cart id or product id"}, 400)

        cart_product = cart_products[0]
        is_valid, errors = check_valid_booking(
            request.data['product_id'], request.data['quantity'],
            cart_product.cart.start_time.strftime(get_date_format()),
            cart_product.cart.end_time.strftime(get_date_format())
        )
        if not is_valid:
            return Response({"message": "Can't update the product quantity", "errors": errors}, 400)

        cart_product.update(quantity=request.data['quantity'])
        return Response({"message": "Product Quantity is updated to {}".format(request.data['quantity'])}, 200)


class CartDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total_carts = Cart.objects.filter(created_by=request.user)
        cart_id_wise_product_details = defaultdict(list)
        total_carts_products = CartProducts.objects.select_related('cart').filter(cart__created_by=request.user)
        if len(total_carts_products) == 0:
            return Response({"message": "Sorry, There are no carts"}, 200)

        product_ids = []
        for each_product in total_carts_products:
            product_ids.append(each_product.product_id)
        product_id_wise_product_details = get_product_details_with_image(product_ids)

        for each_product in total_carts_products:
            cart_id_wise_product_details[each_product.cart_id].append(
                {
                    'id': each_product.id,
                    'product_id':each_product.product_id,
                    'quantity':each_product.quantity,
                    'product_name': product_id_wise_product_details[each_product.product_id]['name'],
                    'product_image_url': product_id_wise_product_details[each_product.product_id]['image_url']
                }
            )

        all_carts = []
        for each_cart in total_carts:
            each_cart_details = \
                {
                    'cart_id': each_cart.id, 'type': each_cart.entity_type,
                    'start_time': each_cart.start_time, 'end_time': each_cart.end_time,
                    'products': cart_id_wise_product_details[each_cart.id]
                }
            all_carts.append(each_cart_details)
        return Response(all_carts, 200)


class DeleteProductFromCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CartProducts.objects.all()
    serializer_class = CartProductsSerializer


class DeleteCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CheckAvailabilityOfAllProducts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        all_cart_products = CartProducts.objects.select_related('cart')\
                            .filter(cart__created_by=request.user)
        out_of_stock_products = defaultdict(list)
        for each_product in all_cart_products:
            is_valid, errors = check_valid_booking(
                each_product.product_id, each_product.quantity,
                each_product.cart.start_time.strftime(get_date_format()),
                each_product.cart.end_time.strftime(get_date_format())
            )
            if not is_valid:
                out_of_stock_products[each_product.cart.id].append({each_product.product_id:errors})
        return Response(out_of_stock_products, 200)
