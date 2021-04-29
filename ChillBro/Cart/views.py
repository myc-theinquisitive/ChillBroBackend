from django.shortcuts import render
from .models import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .wrapper import valid_product
# Create your views here.


class CreateCart(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = CreateCartSerializer(data=request.data)
        if input_serializer.is_valid():
            entity_id, entity_type = valid_product(request.data['product_id'], request.data['quantity'], \
                          request.data['start_time'], request.data['end_time'])
            if entity_id is None:
                return Response({"message": entity_type})
            try:
                cart = Cart.objects.get(entity_id=entity_id, entity_type=entity_type, start_time=request.data['start_time'],\
                                    end_time=request.data['end_time'], user= request.user)
            except:
                serializer = CartSerializer()
                cart = serializer.create({'entity_id': entity_id, 'entity_type': entity_type,\
                                      'start_time':request.data['start_time'],'end_time':request.data['end_time'],\
                                      'user': request.user})
            cart_product_serializer = CartProductsSerializer()
            cart_product = cart_product_serializer.create({"cart":cart, "product_id":request.data['product_id'],
                                                           "quantity":request.data['quantity']})
            return Response({"message":"success"},200)
        else:
            return Response(input_serializer.errors, 400)


class UpdateCartProductQuantity(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        cart_product = CartProducts.objects.select_related('cart')\
                        .filter(cart=request.data['cart'], product_id = request.data['product_id'])
        if len(cart_product) == 0:
            return Response({"message":"invalid cart id or product id"}, 400)
        entity_id, entity_type = valid_product(request.data['product_id'], request.data['quantity'], \
                                               cart_product[0].cart.start_time, cart_product[0].cart.end_time)
        if entity_id is None:
            return Response({"message": entity_type})
        cart_product.update(quantity=request.data['quantity'])
        return Response({"message":"success"},200)


class CartDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total_carts = Cart.objects.filter(user=request.user)
        all_carts_products = {}
        total_carts_products = CartProducts.objects.select_related('cart').filter(cart__user=request.user)
        for each_product in total_carts_products:
            all_carts_products[each_product.cart_id] = all_carts_products.get(each_product.cart_id,[])+[
                {'id':each_product.id,'product_id':each_product.product_id, 'quantity':each_product.quantity}
            ]
        all_carts = []
        for each_cart in total_carts:
            each_cart_details = {'cart_id': each_cart.id, 'type': each_cart.entity_type,
                                 'start_time': each_cart.start_time, 'end_time': each_cart.end_time,
                                 'products': all_carts_products[each_cart.id]}
            all_carts.append(each_cart_details)
        return Response(all_carts,200)


class DeleteProductFromCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CartProducts.objects.all()
    serializer_class = CartProductsSerializer


class DeleteCart(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CheckAvailabilityOfAllProducts(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        all_cart_products = CartProducts.objects.select_related('cart')\
                            .filter(cart__user=request.user)
        out_of_stock_products ={}
        for each_product in all_cart_products:
            valid, comment = valid_product(each_product.product_id, each_product.quantity, \
                                                   each_product.cart.start_time, each_product.cart.end_time)
            if valid is None:
                out_of_stock_products[each_product.cart.id] = {each_product.product_id:comment}
        return Response(out_of_stock_products, 200)
