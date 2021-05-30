from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .wrapper import check_valid_booking, get_product_details_with_image, check_valid_product, \
    get_product_id_wise_product_details, get_discounted_value, create_multiple_bookings_from_cart
from .helpers import get_date_format
from collections import defaultdict
# Create your views here.


class AddProductToCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)
        entity_id, entity_type = check_valid_product(request.data['product_id'])
        if entity_id is None and entity_type is None:
            return Response({"message": "Can't add product to cart", "errors": "Invalid Product"})
        is_valid, errors = check_valid_booking(request.data['product_id'], request.data['quantity'],
                                               request.data['size'], request.data['combo_products'],
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
        combo_products = request.data['combo_products']
        is_combo = False
        if len(combo_products) > 0:
            is_combo = True
        cart_product_serializer = CartProductsSerializer()
        cart_product_id = cart_product_serializer.create(
            {
                "cart": cart,
                "product_id": request.data['product_id'],
                "quantity": request.data['quantity'],
                "size": request.data['size'],
                "is_combo": is_combo
            }
        )

        if len(combo_products) > 0:
            combo_cart_products = []
            for each_combo_product in combo_products:
                combo_cart_products.append({
                    "cart": cart,
                    "product_id": each_combo_product['product_id'],
                    "quantity": each_combo_product['quantity'],
                    "size": each_combo_product['size'],
                    "is_combo": True,
                    "hidden" : True,
                    "parent_cart_product" : cart_product_id
                })
            cart_product_serializer.bulk_create(combo_cart_products)

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
            request.data['size'], request.data['combo_products'],
            cart_product.cart.start_time.strftime(get_date_format()),
            cart_product.cart.end_time.strftime(get_date_format())
        )
        if not is_valid:
            return Response({"message": "Can't update the product quantity", "errors": errors}, 400)
        cart_products.update(quantity=request.data['quantity'])
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
            combo_products = []
            if each_product.hidden is False:
                if each_product.is_combo:
                    for each_combo_product in total_carts_products:
                        if each_combo_product.parent_cart_product_id == each_product.id:
                            combo_products.append({
                                "product_id": each_combo_product.product_id,
                                "quantity": each_combo_product.quantity,
                                "size": each_combo_product.size,
                                "combo_products": []
                            })
                cart_id_wise_product_details[each_product.cart_id].append(
                    {
                        'id': each_product.id,
                        'product_id':each_product.product_id,
                        'quantity':each_product.quantity,
                        'size': each_product.size,
                        'is_combo' : each_product.is_combo,
                        'combo_products': combo_products,
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
        return Response({"results":all_carts}, 200)


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
            combo_products = []
            if each_product.hidden is False:
                if each_product.is_combo:
                    for each_combo_product in all_cart_products:
                        if each_combo_product.parent_cart_product_id == each_product.id:
                            combo_products.append({
                                "product_id": each_combo_product.product_id,
                                "quantity": each_combo_product.quantity,
                                "size": each_combo_product.size,
                                "combo_products":[]
                            })
                is_valid, errors = check_valid_booking(
                    each_product.product_id, each_product.quantity,
                    each_product.size, combo_products,
                    each_product.cart.start_time.strftime(get_date_format()),
                    each_product.cart.end_time.strftime(get_date_format())
                )
                if not is_valid:
                    out_of_stock_products[each_product.cart.id].append({each_product.product_id:errors})
        return Response(out_of_stock_products, 200)


class CheckoutCart(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = CheckoutCartSerializer(data=request.data)
        if input_serializer.is_valid():
            cart_details = Cart.objects.filter(created_by = request.user, entity_type = request.data['entity_type'] )
            cart_items = CartProducts.objects.select_related('cart') \
                .filter(cart__created_by = request.user, cart__entity_type= request.data['entity_type'])

            if len(cart_details) == 0:
                return Response({"message": "Can't checkout","errors":"Sorry, no products in cart"})

            entity_ids = []
            for each_cart in cart_details:
                entity_ids.append(each_cart.entity_id)

            product_ids = []
            for each_product in cart_items:
                if not each_product.hidden:
                    product_ids.append(each_product.product_id)
            product_details = get_product_id_wise_product_details(product_ids)
            total_products_value = 0
            for each_product in cart_items:
                if not each_product.hidden:
                    total_products_value += product_details[each_product.product_id]['price'] * each_product.quantity

            coupon = request.data['coupon']
            total_coupon_value = 0

            if len(request.data['coupon'])>0:
                coupon = get_discounted_value(
                coupon, request.user, product_ids, entity_ids, request.data['entity_type'], total_products_value)
                if not coupon['is_valid']:
                    return Response({"message": "Can't create the booking", "errors": coupon['errors']}, 400)
                total_coupon_value = total_products_value - coupon['discounted_value']

            combo_products_details = defaultdict(list)

            for each_cart_product in cart_items:
                if each_cart_product.hidden:
                    combo_products_details[each_cart_product.cart_id+","+each_cart_product.parent_cart_product.product_id].append(
                        {
                            "product_id": each_cart_product.product_id,
                            "quantity": each_cart_product.quantity,
                            "size": each_cart_product.size,
                            "combo_products": []
                        }
                    )

            cart_products_for_bookings = defaultdict(list)

            for each_cart_product in cart_items:
                if not each_cart_product.hidden:
                    if each_cart_product.is_combo :
                        combo_products = combo_products_details[each_cart_product.cart_id+","+each_cart_product.product_id]
                    else:
                        combo_products = []
                    coupon_value_for_each_product = 0
                    if total_coupon_value >0:
                        coupon_value_for_each_product = (float(total_coupon_value)/100)*((float(product_details[each_cart_product.product_id]['price'])/float(total_products_value))*100)*each_cart_product.quantity

                    cart_products_for_bookings[each_cart_product.cart_id].append({
                            "product_id": each_cart_product.product_id,
                            "quantity": each_cart_product.quantity,
                            "size": each_cart_product.size,
                            "combo_products":combo_products,
                            "coupon_value": coupon_value_for_each_product
                        })

            final_cart_details = defaultdict()
            for each_cart in cart_details:
                final_cart_details[each_cart.id] = {
                    "coupon": coupon,
                    "created_by": request.user,
                    "entity_id": each_cart.entity_id,
                    "entity_type": each_cart.entity_type,
                    "start_time": each_cart.start_time.strftime(get_date_format()),
                    "end_time": each_cart.end_time.strftime(get_date_format()),
                    "products": cart_products_for_bookings[each_cart.id],
                    "payment_mode":"ONLINE",
                    "product_details": product_details
                }
            # return Response(final_cart_details)
            is_valid, errors = create_multiple_bookings_from_cart(final_cart_details)
            if is_valid:
                cart_details.delete()
                return Response({"message": "Successfully created {} bookings".format(len(final_cart_details))})
            else:
                return Response({"message": "Can't create bookings","errors": errors})
        else:
            return Response({"message":"Cant checkout the cart", "errors":input_serializer.errors},400)