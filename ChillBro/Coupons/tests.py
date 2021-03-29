import pytest
from freezegun import freeze_time
from .models import CouponUser, Coupon, CouponUsage
from .serializers import CouponSerializer
from .views import get_discounted_value, use_coupon, get_available_coupons, retrieve_coupon_from_db
from .validations import validate_coupon
from django.contrib.auth import get_user_model
import random
import string


def get_random_number():
    return random.randint(1000, 9999)


def get_random_text():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


class DummyRequestUser:
    def __init__(self, user):
        self.user = user


@pytest.mark.django_db
def create_coupon(code="CouponCode", discount_value=50, discount_is_percentage=True,
                  max_value_if_percentage=100, users=None, all_users=True,
                  entities=None, all_entities=True, products=None, all_products=True,
                  max_uses=10, is_infinite=True, uses_per_user=10,
                  start_time="2021-01-01T00:00:00", end_time="2021-12-31T00:00:00",
                  is_active=True, minimum_order_value=100):

    coupon_title = "Coupon Title"
    coupon_description = "Coupon Description"
    coupon_tc = "[\"Terms and Conditions 1\", \"Terms and Conditions 2\"]"

    users = users if users else []
    entities = entities if entities else []
    products = products if products else []

    coupon_data = {
        "code": code,
        "title": coupon_title,
        "description": coupon_description,
        "terms_and_conditions": coupon_tc,
        "discount": {
            "value": discount_value,
            "is_percentage": discount_is_percentage,
            "max_value_if_percentage": max_value_if_percentage
        },
        "ruleset": {
            "allowed_users": {
                "users": users,
                "all_users": all_users
            },
            "allowed_entities": {
                "entities": entities,
                "all_entities": all_entities
            },
            "allowed_products": {
                "products": products,
                "all_products": all_products
            },
            "max_uses": {
                "max_uses": max_uses,
                "is_infinite": is_infinite,
                "uses_per_user": uses_per_user
            },
            "validity": {
                "start_date": start_time,
                "end_date": end_time,
                "is_active": is_active,
                "minimum_order_value": minimum_order_value
            }
        }
    }

    coupon_serializer = CouponSerializer()
    UserModel = get_user_model()
    random_email = get_random_text() + "@gmail.com"
    user = UserModel.objects.create(id=get_random_number(), email=random_email)

    coupon_serializer.context['request'] = DummyRequestUser(user)
    return coupon_serializer.create(coupon_data)


@pytest.mark.django_db
def test_get_discount():

    # Discount with value 50Rs
    coupon_with_value = create_coupon(code="DISCVALUE", discount_value=50, discount_is_percentage=False)

    new_price = get_discounted_value(coupon_with_value, 200)
    assert new_price == 150

    new_price = get_discounted_value(coupon_with_value, 100)
    assert new_price == 50

    # Discount with percentage 50% and max discount of 200
    coupon_with_percent = create_coupon(code="DISCPERCENT", discount_value=50,
                                        discount_is_percentage=True, max_value_if_percentage=100)

    new_price = get_discounted_value(coupon_with_percent, 200)
    assert new_price == 100

    new_price = get_discounted_value(coupon_with_percent, 500)
    assert new_price == 400


@pytest.mark.django_db
def test_use_coupon():

    users = "[\"1\"]"
    UserModel = get_user_model()
    user = UserModel.objects.create(id="1")
    coupon_for_user = create_coupon(code="UserCoupon", users=users)

    try:
        coupon_user = CouponUser.objects.get(coupon=coupon_for_user, user=user)
        coupon_user_before_usage = coupon_user.times_used
    except CouponUser.DoesNotExist:
        coupon_user_before_usage = 0

    coupon_before_usage = coupon_for_user.times_used
    discount_obtained = use_coupon(coupon_for_user, user, "123", 300)

    coupon_user = CouponUser.objects.get(coupon=coupon_for_user, user=user)
    coupon_user_after_usage = coupon_user.times_used
    coupon_for_user = Coupon.objects.get(code="UserCoupon")
    coupon_after_usage = coupon_for_user.times_used

    assert discount_obtained == 100
    assert coupon_before_usage + 1 == coupon_after_usage
    assert coupon_user_before_usage + 1 == coupon_user_after_usage

    coupon_usage = CouponUsage.objects.get(coupon_user=coupon_user, order_id="123")
    assert coupon_usage.discount_obtained == 100


@pytest.mark.django_db
def test_validate_coupon_for_user():

    users = "[\"1\"]"
    UserModel = get_user_model()
    create_coupon(code="UserCoupon", users=users, all_users=False)

    # valid user test
    user = UserModel.objects.create(id="1", email="test1@gmail.com")
    response = validate_coupon(retrieve_coupon_from_db("UserCoupon"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"

    # invalid user test
    user = UserModel.objects.create(id="2", email="test2@gmail.com")
    response = validate_coupon(retrieve_coupon_from_db("UserCoupon"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Invalid coupon for this User!"

    create_coupon(code="ALLUser", all_users=True)

    # all users allowed test
    response = validate_coupon(retrieve_coupon_from_db("ALLUser"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"


@pytest.mark.django_db
def test_validate_coupon_for_entity():

    entities = "[\"1\"]"
    UserModel = get_user_model()
    create_coupon(code="EntityCoupon", entities=entities, all_entities=False)
    user = UserModel.objects.create(id="1", email="test1@gmail.com")

    # valid entity test
    response = validate_coupon(retrieve_coupon_from_db("EntityCoupon"), user, ["1"], ["Product"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"

    # invalid entity test
    response = validate_coupon(retrieve_coupon_from_db("EntityCoupon"), user, ["2"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Invalid coupon for this Entities!"

    # some valid entities and some invalid entities test
    response = validate_coupon(retrieve_coupon_from_db("EntityCoupon"), user, ["1", "2"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Invalid coupon for this Entities!"

    create_coupon(code="ALLEntities", all_entities=True)

    # all entities allowed test
    response = validate_coupon(retrieve_coupon_from_db("ALLEntities"), user, ["3"], ["Product"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"


@pytest.mark.django_db
def test_validate_coupon_for_product():

    products = "[\"1\"]"
    UserModel = get_user_model()
    create_coupon(code="Product", products=products, all_products=False)
    user = UserModel.objects.create(id="1", email="test1@gmail.com")

    # valid product test
    response = validate_coupon(retrieve_coupon_from_db("Product"), user, ["Entity"], ["1"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"

    # invalid product test
    response = validate_coupon(retrieve_coupon_from_db("Product"), user, ["Entity"], ["2"], 500)
    assert response["valid"] is False
    assert response["message"] == "Invalid coupon for this Products!"

    # some valid products and some invalid products test
    response = validate_coupon(retrieve_coupon_from_db("Product"), user, ["Entity"], ["1", "2"], 500)
    assert response["valid"] is False
    assert response["message"] == "Invalid coupon for this Products!"

    create_coupon(code="ALLProducts", all_products=True)

    # all products allowed test
    response = validate_coupon(retrieve_coupon_from_db("ALLProducts"), user, ["Entity"], ["3"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"


@pytest.mark.django_db
def test_validate_coupon_max_uses():

    UserModel = get_user_model()
    user = UserModel.objects.create(id="1", email="test@gmail.com")

    # test max uses for coupon
    max_uses_coupon = create_coupon(code="MaxUses", max_uses=1, is_infinite=False)
    use_coupon(max_uses_coupon, user, "123", 300)

    response = validate_coupon(retrieve_coupon_from_db("MaxUses"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Coupon uses exceeded!"

    # test infinite uses
    infinite_uses_coupon = create_coupon(code="InfUses", is_infinite=True)
    use_coupon(infinite_uses_coupon, user, "123", 300)
    use_coupon(infinite_uses_coupon, user, "234", 400)
    use_coupon(infinite_uses_coupon, user, "345", 500)

    response = validate_coupon(retrieve_coupon_from_db("InfUses"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"

    # test max user per coupon per user
    max_user_uses_coupon = create_coupon(code="MaxUserUses", is_infinite=False, max_uses=100, uses_per_user=2)
    use_coupon(max_user_uses_coupon, user, "123", 300)
    use_coupon(max_user_uses_coupon, user, "234", 400)

    response = validate_coupon(retrieve_coupon_from_db("MaxUserUses"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Coupon uses exceeded for this User!"


@pytest.mark.django_db
@freeze_time('2021-01-01')
def test_validate_validity():

    UserModel = get_user_model()
    user = UserModel.objects.create(id="1", email="test@gmail.com")

    # test start date validation
    create_coupon(code="StartDate", start_time="2021-01-02T00:00:00")

    response = validate_coupon(retrieve_coupon_from_db("StartDate"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Coupon Not Active YET!"

    # test end date validation
    create_coupon(code="EndDate", end_time="2020-12-01T00:00:00")

    response = validate_coupon(retrieve_coupon_from_db("EndDate"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Coupon Expired!"

    # test is active validation
    create_coupon(code="IsActive", is_active=False)

    response = validate_coupon(retrieve_coupon_from_db("IsActive"), user, ["Entity"], ["Product"], 500)
    assert response["valid"] is False
    assert response["message"] == "Coupon is not active"

    # test minimum order value validation
    create_coupon(code="MinVal", minimum_order_value=500)

    response = validate_coupon(retrieve_coupon_from_db("MinVal"), user, ["Entity"], ["Product"], 300)
    assert response["valid"] is False
    assert response["message"] == "Minimum order value to avail the coupon is 500"

    # test valid coupon
    create_coupon(code="Valid", start_time="2020-12-01T00:00:00", end_time="2021-02-01T00:00:00",
                  is_active=True, minimum_order_value=300)

    response = validate_coupon(retrieve_coupon_from_db("Valid"), user, ["Entity"], ["Product"], 300)
    assert response["valid"] is True
    assert response["message"] == "Valid Coupon!"


@pytest.mark.django_db
@freeze_time('2021-02-01')
def test_available_coupons():
    # coupon available for all
    create_coupon(code="NEWCOUPON")
    # coupon available for current user
    create_coupon(code="NEWCOUPON2", users=["1"], all_users=False)
    # coupon with not enough order value
    create_coupon(code="NEWCOUPON3", minimum_order_value=500)
    # coupon not available for current user
    create_coupon(code="NEWCOUPON4", users=["2"], all_users=False)
    # coupon not available for current entity
    create_coupon(code="NEWCOUPON5", users=["1"], all_users=False, entities=["4"], all_entities=False)
    # coupon not available for current product
    create_coupon(code="NEWCOUPON6", entities=["2"], all_entities=False, products=["4"], all_products=False)

    response = get_available_coupons("1", ["2"], ["3"], 300)

    expected_response = {
        'NEWCOUPON': {
            'coupon_code': 'NEWCOUPON',
            'available': True,
            'reason': ''
        },
        'NEWCOUPON2': {
            'coupon_code': 'NEWCOUPON2',
            'available': True,
            'reason': ''
        },
        'NEWCOUPON3': {
            'coupon_code': 'NEWCOUPON3',
            'available': False,
            'reason': 'Add Rs:200 more to avail the offer'
        }
    }

    for coupon in response:
        assert coupon["coupon_code"] in expected_response.keys()
        expected_coupon_data = expected_response[coupon["coupon_code"]]
        assert coupon["available"] == expected_coupon_data["available"]
        assert coupon["reason"] == expected_coupon_data["reason"]

