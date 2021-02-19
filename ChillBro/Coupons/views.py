from rest_framework import status, generics, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .wrapper import get_entity_model
from .models import CouponUser, CouponUsage, CouponUserUsages, Coupon
from .searializers import UseCouponSerializer, DiscountSerializer
from .validations import validate_coupon


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
    coupon_user.times_used += 1
    coupon_user.save()

    new_price = get_discounted_value(coupon, order_value)
    discount_obtained = order_value - new_price
    coupon_usage = CouponUsage(coupon_user=coupon_user, order_id=order_id,
                               discount_obtained=discount_obtained)
    coupon_usage.save()

    CouponUserUsages.objects.create(coupon_user=coupon_user, coupon_usage=coupon_usage)

    coupon.times_used += 1
    coupon.save()

    return discount_obtained


class Discount(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DiscountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        entity_id = serializer.data["entity_id"]
        coupon_code = serializer.data['coupon_code']
        order_value = serializer.data['order_value']

        entity_model = get_entity_model()
        entity = entity_model.objects.get(id=entity_id)
        validation_data = validate_coupon(coupon_code=coupon_code, user=user, entity=entity, order_value=order_value)

        if not validation_data['valid']:
            content = {'message': validation_data['message']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        coupon = Coupon.objects.get(code=coupon_code)
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
        entity_id = serializer.data["entity_id"]
        coupon_code = serializer.data['coupon_code']
        order_id = serializer.data['order_id']
        order_value = serializer.data['order_value']

        entity_model = get_entity_model()
        entity = entity_model.objects.get(id=entity_id)
        validation_data = validate_coupon(coupon_code=coupon_code, user=user, entity=entity, order_value=order_value)

        if not validation_data['valid']:
            content = {'message': validation_data['message']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        coupon = Coupon.objects.get(code=coupon_code)
        discount_obtained = use_coupon(coupon=coupon, user=user, order_id=order_id, order_value=order_value)
        content = {'message': 'You saved {0}'.format(discount_obtained)}
        return Response(content, status=status.HTTP_200_OK)
