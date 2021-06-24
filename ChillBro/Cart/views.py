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

def is_product_valid(product_details, product_id, quantity, size, combo_product_details):
    is_valid = True
    errors = defaultdict(list)
    if quantity < 1:
        is_valid = False
        errors[product_id].append("Quantity must be greater than zero")
    if product_details[product_id]['has_sizes']:
        product_sizes_details = product_details[product_id]['size_products']
        try:
            products_quantity = product_sizes_details[size]
        except:
            is_valid = False
            errors[product_id].append("Invalid Size")

    if product_details[product_id]["is_combo"]:
        combo_products_data = product_details[product_id]['combo_products']
        if len(combo_products_data) != len(combo_product_details):
            is_valid = False
            errors[product_id].append("Invalid combo product data")

        for each_combo_product in combo_product_details:
            try:
                products_quantity = combo_products_data[each_combo_product]
            except:
                is_valid = False
                errors[product_id].append("Invalid combo product data")

    return is_valid, errors


class AddProductToCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToCartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add product to cart", "errors": input_serializer.errors}, 400)
        product_id = request.data['product_id']
        quantity = request.data['quantity']
        size = request.data['size']
        combo_product_details = request.data['combo_product_details']
        entity_id, entity_type = check_valid_product(product_id)
        product_ids = [product_id]
        product_details = get_product_id_wise_product_details(product_ids)
        products = []

        is_valid, errors = is_product_valid(product_details, product_id, quantity, size, combo_product_details)
        if not is_valid:
            return Response({"message": "Can't add product to cart","errors": errors})

        if product_details[product_id]["is_combo"]:
            combo_products_data = product_details[product_id]['combo_products']

            for each_combo_product in combo_products_data:
                combo_product = {
                    "product_id": each_combo_product,
                    "quantity": combo_products_data[each_combo_product]['quantity'] * quantity,
                    "size": combo_product_details[each_combo_product]
                }
                products.append(combo_product)
        elif product_details[product_id]["has_sub_products"]:
            sub_products = product_details[product_id]["sub_products"]
            for each_sub_product in sub_products:
                products.append({
                    "product_id": each_sub_product,
                    "quantity": 1,
                    "size": ""
                })
        else:
            products.append({
                "product_id": product_id,
                "quantity": quantity,
                "size": request.data['size']
            })

        if entity_id is None and entity_type is None:
            return Response({"message": "Can't add product to cart", "errors": "Invalid Product"})

        try:
            cart = Cart.objects.get(entity_id=entity_id, entity_type=entity_type, start_time=request.data['start_time'],
                                    end_time=request.data['end_time'], created_by=request.user)
            is_cart_exist = True
        except ObjectDoesNotExist:
            is_cart_exist = False

        if not is_cart_exist:
            is_valid, errors = check_valid_booking(products, request.data['start_time'], request.data['end_time'])
        else:
            cart_products = CartProducts.objects.filter(cart_id=cart,product_id=product_id)
            all_cart_products = []

            for each_product in cart_products:
                if each_product.product_id == product_id:
                    if each_product.parent_cart_product_id is None:
                        return Response({"message": "Product already exists in cart", "cart_id": cart.id}, 200)
                    if not each_product.is_combo:
                        all_cart_products.append({
                            "product_id": each_product.product_id,
                            "quantity": each_product.quantity,
                            "size": each_product.size
                        })
            all_cart_products += products
            is_valid, errors = check_valid_booking(combine_products(all_cart_products), request.data['start_time'],
                                                   request.data['end_time'])
        if not is_valid:
            return Response({"message": "Can't add product to cart", "errors": errors}, 400)

        if not is_cart_exist:
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
        is_combo, has_sub_products = False, False
        if product_details[product_id]["is_combo"]:
            is_combo = True
        if product_details[product_id]["has_sub_products"]:
            has_sub_products = True
        cart_product_serializer = CartProductsSerializer()
        cart_product_id = cart_product_serializer.create({
                "cart": cart,
                "product_id": request.data['product_id'],
                "quantity": request.data['quantity'],
                "size": request.data['size'],
                "is_combo": is_combo,
                "has_sub_products": has_sub_products
            })

        if is_combo or has_sub_products:
            combo_cart_products = []
            for each_combo_product in products:
                combo_cart_products.append({
                    "cart": cart,
                    "product_id": each_combo_product['product_id'],
                    "quantity": each_combo_product['quantity'],
                    "size": each_combo_product['size'],
                    "is_combo": False,
                    "hidden": True,
                    "parent_cart_product": cart_product_id
                })
            cart_product_serializer.bulk_create(combo_cart_products)

        return Response({"message": "Product added to cart successfully", "cart_id": cart.id}, 200)


class UpdateCartProductQuantity(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        product_id = request.data['product_id']
        quantity = request.data['quantity']
        size = request.data['size']
        product_details = get_product_id_wise_product_details([product_id])
        combo_product_details = request.data['combo_product_details']
        products = []

        is_valid, errors = is_product_valid(product_details, product_id, quantity, size, combo_product_details)
        if not is_valid:
            return Response({"message": "Can't add product to cart","errors": errors})

        cart_products = CartProducts.objects.select_related('cart') \
            .filter(cart=request.data['cart'], product_id=product_id)
        if len(cart_products) == 0:
            return Response({"message": "Can't update the product quantity",
                             "errors": "invalid cart id or product id"}, 400)

        cart_product = cart_products[0]

        if product_details[product_id]["is_combo"]:
            combo_products_data = product_details[product_id]['combo_products']

            for each_combo_product in combo_products_data:
                combo_product = {
                    "product_id": each_combo_product,
                    "quantity": combo_products_data[each_combo_product]['quantity'] * quantity,
                    "size": combo_product_details[each_combo_product]
                }
                products.append(combo_product)
        else:
            products.append({
                "product_id": product_id,
                "quantity": quantity,
                "size": request.data['size']
            })

        all_cart_products = []
        for each_product in cart_products:
            if each_product.product_id == product_id and each_product.parent_cart_product_id is not None:
                if not each_product.is_combo:
                    all_cart_products.append({
                        "product_id": each_product.product_id,
                        "quantity": each_product.quantity,
                        "size": each_product.size
                    })
        all_cart_products += products

        is_valid, errors = check_valid_booking(combine_products(all_cart_products),
                                               cart_product.cart.start_time.strftime(get_date_format()),
                                               cart_product.cart.end_time.strftime(get_date_format())
                                               )
        if not is_valid:
            return Response({"message": "Can't update the product quantity", "errors": errors}, 400)
        update_cart_products =[]
        for each_product in cart_products:
            if each_product.parent_cart_product is None and each_product.product_id == product_id:
                update_cart_products.append({"id":each_product.id,"quantity":request.data['quantity'],"size":size})
            elif each_product.parent_cart_product is not None and each_product.parent_cart_product.product_id == product_id:
                update_cart_products.append({"id":each_product.id,"quantity":request.data['quantity'] * \
                                            combo_products_data[each_product.product_id]['quantity'], \
                                            "size":combo_product_details[each_product.product_id]})
        bulk_update_serializer = CartProductsSerializer()
        bulk_update_serializer.bulk_update(update_cart_products)
        return Response({"message": "Product Quantity is updated to {} and size is updated to {}".format(quantity, size)}, 200)


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

        combo_products_details = defaultdict(list)
        for each_cart_product in total_carts_products:
            if each_cart_product.hidden:
                combo_products_details[
                    each_cart_product.cart_id + "," + each_cart_product.parent_cart_product.product_id].append(
                    {
                        "product_id": each_cart_product.product_id,
                        "quantity": each_cart_product.quantity,
                        "size": each_cart_product.size,
                        "combo_products": []
                    }
                )

        for each_product in total_carts_products:
            combo_products = []
            if each_product.hidden is False:
                if each_product.is_combo or each_product.has_sub_products:
                    combo_products = combo_products_details[each_product.cart_id + "," + each_product.product_id]
                cart_id_wise_product_details[each_product.cart_id].append(
                    {
                        'id': each_product.id,
                        'product_id': each_product.product_id,
                        'quantity': each_product.quantity,
                        'size': each_product.size,
                        'is_combo': each_product.is_combo,
                        'has_sub_products': each_product.has_sub_products,
                        'combo_products': combo_products,
                        'product_name': product_id_wise_product_details[each_product.product_id]['name'],
                        'product_image_url': product_id_wise_product_details[each_product.product_id]['images'][0]
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
        return Response({"results": all_carts}, 200)


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
        all_cart_products = CartProducts.objects.select_related('cart') \
            .filter(cart__created_by=request.user)
        out_of_stock_products = defaultdict(list)

        combo_products_details = defaultdict(list)
        for each_cart_product in all_cart_products:
            if each_cart_product.hidden:
                combo_products_details[
                    each_cart_product.cart_id + "," + each_cart_product.parent_cart_product.product_id].append(
                    {
                        "product_id": each_cart_product.product_id,
                        "quantity": each_cart_product.quantity,
                        "size": each_cart_product.size,
                    }
                )

        for each_product in all_cart_products:
            products = []
            if each_product.hidden is False:
                if each_product.is_combo:
                    products = combo_products_details[each_product.cart_id + "," + each_product.product_id]
                else:
                    products.append({
                        "product_id": each_product.product_id,
                        "quantity": each_product.quantity,
                        "size": each_product.size
                    })

                is_valid, errors = check_valid_booking(
                    products,
                    each_product.cart.start_time.strftime(get_date_format()),
                    each_product.cart.end_time.strftime(get_date_format())
                )
                if not is_valid:
                    out_of_stock_products[each_product.cart.id].append({each_product.product_id: errors})
        return Response(out_of_stock_products, 200)


class CheckoutCart(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = CheckoutCartSerializer(data=request.data)
        if input_serializer.is_valid():
            cart_details = Cart.objects.filter(created_by=request.user, entity_type=request.data['entity_type'])
            cart_items = CartProducts.objects.select_related('cart') \
                .filter(cart__created_by=request.user, cart__entity_type=request.data['entity_type'])

            if len(cart_details) == 0:
                return Response({"message": "Can't checkout", "errors": "Sorry, no products in cart"})

            entity_ids = []
            for each_cart in cart_details:
                entity_ids.append(each_cart.entity_id)

            product_ids = []
            for each_product in cart_items:
                product_ids.append(each_product.product_id)
            product_details = get_product_id_wise_product_details(product_ids)

            total_products_value = calculate_total_products_value(cart_items, product_details)

            coupon = request.data['coupon']
            total_coupon_value = 0

            if len(request.data['coupon']) > 0:
                coupon_data = get_discounted_value(
                    coupon, request.user, product_ids, entity_ids, request.data['entity_type'], total_products_value)
                if not coupon_data['is_valid']:
                    return Response({"message": "Can't create the booking", "errors": coupon['errors']}, 400)
                total_coupon_value = total_products_value - coupon_data['discounted_value']

            cart_products_for_bookings = form_each_cart_all_products(cart_items, product_details, total_products_value, total_coupon_value)

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
                }
            final_cart_details['all_product_details'] = product_details

            is_valid, errors = create_multiple_bookings_from_cart(final_cart_details)
            if is_valid:
                cart_details.delete()
                return Response({"message": "Successfully created {} bookings".format(len(final_cart_details))})
            else:
                return Response({"message": "Can't create bookings", "errors": errors})
        else:
            return Response({"message": "Cant checkout the cart", "errors": input_serializer.errors}, 400)


def calculate_coupon_value(total_coupon_value, product_value, total_products_value, quantity):
    return (float(total_coupon_value) / 100) * ((float(product_value) / float(total_products_value)) * 100) * quantity


def combine_products(all_cart_products):
    form_together = defaultdict()
    for each_product in all_cart_products:
        try:
            form_together[each_product['product_id'] + "," + each_product['size']] = {
                "product_id": each_product['product_id'],
                "quantity": form_together[each_product['product_id'] + "," + each_product['size']]['quantity'] + each_product['quantity'],
                "size": each_product['size']
            }
        except:
            form_together[each_product['product_id'] + "," + each_product['size']] = {
                "product_id": each_product['product_id'],
                "quantity": each_product['quantity'],
                "size": each_product['size']
            }
    final_products = []
    for each_product in form_together:
        final_products.append(form_together[each_product])

    return final_products


def form_each_cart_all_products(cart_items, product_details, total_products_value, total_coupon_value):
    cart_products_for_bookings = defaultdict(list)
    for each_cart_product in cart_items:
        if each_cart_product.hidden:
            cart_products_for_bookings[each_cart_product.cart_id].append(
                {
                    "product_id": each_cart_product.product_id,
                    "quantity": each_cart_product.quantity,
                    "size": each_cart_product.size,
                    "parent_booked_product": each_cart_product.parent_cart_product.product_id,
                    "coupon_value": 0,
                    "is_combo": False,
                    "has_sub_products": False
                }
            )
        else:
            coupon_value_for_each_product = 0
            if total_coupon_value > 0:
                coupon_value_for_each_product = calculate_coupon_value(total_coupon_value, \
                    product_details[each_cart_product.product_id]['price'], total_products_value, \
                    each_cart_product.quantity)

            cart_products_for_bookings[each_cart_product.cart_id].append({
                "product_id": each_cart_product.product_id,
                "quantity": each_cart_product.quantity,
                "size": each_cart_product.size,
                "parent_booked_product": None,
                "coupon_value": coupon_value_for_each_product,
                "is_combo": each_cart_product.is_combo,
                "has_sub_products": each_cart_product.has_sub_products
            })

    return cart_products_for_bookings


def calculate_total_products_value(cart_items, product_details):
    total_products_value = 0
    for each_product in cart_items:
        if not each_product.hidden:
            total_products_value += product_details[each_product.product_id]['price'] * each_product.quantity

    return total_products_value