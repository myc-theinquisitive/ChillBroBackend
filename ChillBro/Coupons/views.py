from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CouponUser, CouponUsage, CouponUserUsages, Coupon, CouponHistory
from .serializers import UseCouponSerializer, GetDiscountSerializer, CouponSerializer, \
    CouponHistorySerializer, AvailableCouponForOrderSerializer, AvailableCouponSerializer
from .validations import validate_coupon
from django.db.models import F, Q
from django.utils import timezone
import json
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsGet


def retrieve_coupon_from_db(coupon_code):
    try:
        return Coupon.objects.select_related(
            'discount', 'ruleset__allowed_users', 'ruleset__allowed_entities',
            'ruleset__allowed_products', 'ruleset__allowed_product_types',
            'ruleset__max_uses', 'ruleset__validity').get(code=coupon_code)
    except Coupon.DoesNotExist:
        return None


def convert_json_dumps_fields(coupon):
    users = coupon["ruleset"]["allowed_users"]["users"]
    users = users.replace("'", '"')
    coupon["ruleset"]["allowed_users"]["users"] = json.loads(users)

    entities = coupon["ruleset"]["allowed_entities"]["entities"]
    entities = entities.replace("'", '"')
    coupon["ruleset"]["allowed_entities"]["entities"] = json.loads(entities)

    products = coupon["ruleset"]["allowed_products"]["products"]
    products = products.replace("'", '"')
    coupon["ruleset"]["allowed_products"]["products"] = json.loads(products)

    product_types = coupon["ruleset"]["allowed_product_types"]["product_types"]
    product_types = product_types.replace("'", '"')
    coupon["ruleset"]["allowed_product_types"]["product_types"] = json.loads(product_types)

    terms_and_conditions = coupon["terms_and_conditions"]
    if terms_and_conditions:
        terms_and_conditions = terms_and_conditions.replace("'", '"')
        coupon["terms_and_conditions"] = json.loads(terms_and_conditions)

    return coupon


def get_discounted_value(coupon, order_value):
    discount = coupon.discount

    if discount.is_percentage:
        discount_value = ((order_value * discount.value) / 100)
        if discount_value > discount.max_value_if_percentage:
            discount_value = discount.max_value_if_percentage
        new_price = order_value - discount_value
        new_price = new_price if new_price >= 0.0 else 0.0
    else:
        new_price = order_value - discount.value
        new_price = new_price if new_price >= 0.0 else 0.0

    return new_price


def use_coupon(coupon, user, order_id, order_value):
    coupon_user, created = CouponUser.objects.get_or_create(user=user, coupon=coupon)
    coupon_user.times_used = F('times_used') + 1
    coupon_user.save()

    new_price = get_discounted_value(coupon, order_value)
    discount_obtained = order_value - new_price
    coupon_usage = CouponUsage(coupon_user=coupon_user, order_id=order_id,
                               discount_obtained=discount_obtained)
    coupon_usage.save()

    CouponUserUsages.objects.create(coupon_user=coupon_user, coupon_usage=coupon_usage)

    coupon.times_used = F('times_used') + 1
    coupon.save()

    return discount_obtained


def get_active_coupons_with_all_details():
    current_time = timezone.now()
    coupons = Coupon.objects.select_related(
        'discount', 'ruleset__allowed_users', 'ruleset__allowed_entities',
        'ruleset__allowed_products', 'ruleset__allowed_product_types',
        'ruleset__max_uses', 'ruleset__validity') \
        .filter(Q(Q(times_used__lt=F('ruleset__max_uses__max_uses')) |
                  Q(ruleset__max_uses__is_infinite=True)) &
                Q(Q(ruleset__validity__start_date__lt=current_time) &
                  Q(ruleset__validity__end_date__gt=current_time)) &
                Q(ruleset__validity__is_active=True)
                )
    return coupons


def get_available_coupon_objects(active_coupons, user_id, entity_ids, product_ids, product_types):
    coupons_available = []
    for coupon in active_coupons:
        if not coupon.ruleset.allowed_users.all_users:
            users = coupon.ruleset.allowed_users.users
            if not str(user_id) in users:
                continue

        if not coupon.ruleset.allowed_entities.all_entities:
            entities = coupon.ruleset.allowed_entities.entities
            if not set(entity_ids).issubset(entities):
                continue

        if not coupon.ruleset.allowed_products.all_products:
            products = coupon.ruleset.allowed_products.products
            if not set(product_ids).issubset(products):
                continue

        if not coupon.ruleset.allowed_product_types.all_product_types:
            allowed_product_types = coupon.ruleset.allowed_product_types.product_types
            if not set(product_types).issubset(allowed_product_types):
                continue
        coupons_available.append(coupon)
    return coupons_available


def get_available_coupons_for_user(active_coupons, user_id, entity_ids, product_ids, product_types):
    available_coupons = get_available_coupon_objects(
        active_coupons, user_id, entity_ids, product_ids, product_types)
    coupons_available_for_user = []
    for coupon in available_coupons:
        coupon_data = {
            "coupon_code": coupon.code,
            "title": coupon.title,
            "description": coupon.description,
            "terms_and_conditions": coupon.terms_and_conditions,
            "expiry_data": coupon.ruleset.validity.end_date.strftime("%d %B, %Y")
        }
        coupons_available_for_user.append(coupon_data)
    return coupons_available_for_user


def get_available_coupons_for_order(active_coupons, user_id, entity_ids, product_ids, product_types, order_value):
    available_coupons = get_available_coupon_objects(active_coupons, user_id, entity_ids, product_ids, product_types)
    coupons_available_for_order = []
    for coupon in available_coupons:
        available = True
        reason = ""
        if order_value < coupon.ruleset.validity.minimum_order_value:
            available = False
            reason = "Add Rs:{0} more to avail the offer".format(
                coupon.ruleset.validity.minimum_order_value - order_value)

        coupon_data = {
            "coupon_code": coupon.code,
            "title": coupon.title,
            "description": coupon.description,
            "terms_and_conditions": coupon.terms_and_conditions,
            "available": available,
            "reason": reason
        }
        coupons_available_for_order.append(coupon_data)
    return coupons_available_for_order


class Discount(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetDiscountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        entity_ids = serializer.data["entity_ids"]
        product_ids = serializer.data["product_ids"]
        product_types = serializer.data["product_types"]
        coupon_code = serializer.data['coupon_code']
        order_value = serializer.data['order_value']

        coupon = retrieve_coupon_from_db(coupon_code)
        if coupon:
            validation_data = validate_coupon(coupon=coupon, user=user, entity_ids=entity_ids,
                                              product_types=product_types, product_ids=product_ids,
                                              order_value=order_value)
        else:
            validation_data = {
                "valid": False,
                "message": "Coupon does not exist!"
            }

        if not validation_data['valid']:
            content = {'message': validation_data['message']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        new_price = get_discounted_value(coupon=coupon, order_value=order_value)
        content = {'new_price': new_price}
        return Response(content, status=status.HTTP_200_OK)


class UseCoupon(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UseCouponSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        entity_ids = serializer.data["entity_ids"]
        product_ids = serializer.data["product_ids"]
        product_types = serializer.data["product_types"]
        coupon_code = serializer.data['coupon_code']
        order_id = serializer.data['order_id']
        order_value = serializer.data['order_value']

        coupon = retrieve_coupon_from_db(coupon_code)
        if coupon:
            validation_data = validate_coupon(coupon=coupon, user=user, entity_ids=entity_ids,
                                              product_types=product_types, product_ids=product_ids,
                                              order_value=order_value)
        else:
            validation_data = {
                "valid": False,
                "message": "Coupon does not exist!"
            }

        if not validation_data['valid']:
            content = {'message': validation_data['message']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        discount_obtained = use_coupon(coupon=coupon, user=user, order_id=order_id, order_value=order_value)
        content = {'message': 'You saved {0}'.format(discount_obtained)}
        return Response(content, status=status.HTTP_200_OK)


class CouponList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet,)
    serializer_class = CouponSerializer
    queryset = Coupon.objects.select_related(
        'discount', 'ruleset__allowed_users', 'ruleset__allowed_entities',
        'ruleset__allowed_products', 'ruleset__allowed_product_types',
        'ruleset__max_uses', 'ruleset__validity').all()

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        for coupon in response.data["results"]:
            convert_json_dumps_fields(coupon)
        return response


class CouponDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet,)
    serializer_class = CouponSerializer
    queryset = Coupon.objects.select_related(
        'discount', 'ruleset__allowed_users', 'ruleset__allowed_entities', 'ruleset__allowed_products',
        'ruleset__allowed_product_types', 'ruleset__max_uses', 'ruleset__validity').all()
    lookup_field = "code"

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, args, kwargs)
        coupon = response.data
        convert_json_dumps_fields(coupon)
        return response


class CouponHistoryList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee, )
    serializer_class = CouponHistorySerializer

    def get(self, request, *args, **kwargs):
        try:
            Coupon.objects.get(code__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Coupon!!!"}, 400)

        self.queryset = CouponHistory.objects.filter(code__icontains=kwargs["slug"]) \
            .select_related('discount', 'ruleset__allowed_users', 'ruleset__allowed_entities',
                            'ruleset__allowed_products', 'ruleset__allowed_product_types',
                            'ruleset__max_uses', 'ruleset__validity').all()
        response = super().get(request, args, kwargs)

        for coupon in response.data["results"]:
            convert_json_dumps_fields(coupon)
        return response


class AvailableCouponsForOrder(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AvailableCouponForOrderSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        entity_ids = serializer.data["entity_ids"]
        product_types = serializer.data["product_types"]
        product_ids = serializer.data["product_ids"]
        order_value = serializer.data['order_value']

        active_coupons = get_active_coupons_with_all_details()
        coupons = get_available_coupons_for_order(
            active_coupons=active_coupons, user_id=str(user.id), entity_ids=entity_ids,
            product_types=product_types, product_ids=product_ids, order_value=order_value)

        for coupon in coupons:
            terms_and_conditions = coupon["terms_and_conditions"]
            if terms_and_conditions:
                terms_and_conditions = terms_and_conditions.replace("'", '"')
                coupon["terms_and_conditions"] = json.loads(terms_and_conditions)

        return Response({"results": coupons}, status=status.HTTP_200_OK)


class AvailableCoupons(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AvailableCouponSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        entity_ids = serializer.data["entity_ids"]
        product_types = serializer.data["product_types"]
        product_ids = serializer.data["product_ids"]

        active_coupons = get_active_coupons_with_all_details()
        coupons = get_available_coupons_for_user(
            active_coupons=active_coupons, user_id=str(user.id), entity_ids=entity_ids,
            product_types=product_types, product_ids=product_ids)

        for coupon in coupons:
            terms_and_conditions = coupon["terms_and_conditions"]
            if terms_and_conditions:
                terms_and_conditions = terms_and_conditions.replace("'", '"')
                coupon["terms_and_conditions"] = json.loads(terms_and_conditions)

        return Response({"results": coupons}, status=status.HTTP_200_OK)
