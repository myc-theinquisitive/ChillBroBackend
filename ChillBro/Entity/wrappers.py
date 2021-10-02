import decimal
from Address.exportapi import create_address, get_address_details, update_address, filter_by_city
from UserApp.exportapi import get_employee_details_for_entities, entity_ids_for_employee
from collections import defaultdict
from django.db.models import Subquery, OuterRef, FloatField, PositiveIntegerField
from WishList.exportapis import get_wishlist_entity_ids
from ReviewsRatings.exportapi import get_rating_stats_for_related_ids, \
    get_rating_type_wise_average_rating_for_related_ids, get_latest_ratings_for_related_ids

# from .export_apis import get_entity_details_for_entity_ids


def post_create_address(address_data):
    return create_address(address_data)


def update_address_for_address_id(address_id, address_data):
    return update_address(address_id, address_data)


def get_total_products_count_in_entities(entity_ids):
    from Product.exportapi import total_products_count_in_entities
    return total_products_count_in_entities(entity_ids)


def get_address_details_for_address_ids(address_ids):
    return get_address_details(address_ids)


def get_entity_id_wise_employees(entity_ids):
    employees = get_employee_details_for_entities(entity_ids)
    entity_id_wise_employees = defaultdict(list)
    for employee in employees:
        entity_id_wise_employees[employee["entity_id"]].append(employee)
    return entity_id_wise_employees


def filter_address_ids_by_city(address_ids, city):
    return filter_by_city(address_ids, city)


def get_entity_ids_for_employee(user_id):
    return entity_ids_for_employee(user_id)


def average_rating_query_for_entity(entity_id):
    from Bookings.exportapi import average_ratings_for_entity_based_on_bookings
    return average_ratings_for_entity_based_on_bookings(entity_id)


def entity_products_starting_price_query(entity_id):
    from Product.exportapi import seller_products_starting_price_query
    return seller_products_starting_price_query(entity_id)


def get_entity_id_wise_starting_price(entity_ids):
    from Product.exportapi import get_sellers_product_stating_price
    entities_starting_price = get_sellers_product_stating_price(entity_ids)

    entity_id_wise_starting_price = defaultdict(decimal.Decimal)
    for entity_starting_price in entities_starting_price:
        entity_id = entity_starting_price.pop("seller_id", None)
        entity_id_wise_starting_price[entity_id] = entity_starting_price["starting_price"]

    return entity_id_wise_starting_price


def get_entities_with_average_rating(entity_ids):
    from Bookings.exportapi import average_ratings_for_entity_based_on_bookings, \
        total_reviews_for_entity_based_on_bookings
    from .models import MyEntity
    return MyEntity.objects.filter(id__in=entity_ids) \
        .annotate(
            avg_rating=Subquery(
                queryset=average_ratings_for_entity_based_on_bookings(OuterRef(OuterRef('id'))),
                output_field=FloatField()
            ),
            total_reviews=Subquery(
                queryset=total_reviews_for_entity_based_on_bookings(OuterRef(OuterRef('id'))),
                output_field=PositiveIntegerField()
            )
        ).values('id', 'avg_rating', 'total_reviews')


def get_entity_id_wise_average_rating(entity_ids):
    entity_reviews = get_entities_with_average_rating(entity_ids)

    entity_id_wise_average_rating = defaultdict(dict)
    for entity_review in entity_reviews:
        entity_id = entity_review.pop("id", None)
        entity_id_wise_average_rating[entity_id] = entity_review

    for entity_id in entity_ids:
        if not entity_id_wise_average_rating[entity_id]['total_reviews']:
            entity_id_wise_average_rating[entity_id] = {
                "avg_rating": 0,
                "total_reviews": 0
            }

    return entity_id_wise_average_rating


def get_entity_id_wise_wishlist_status(user_id, entity_ids):
    entity_id_wise_wishlist_status = defaultdict(bool)
    wishlist_entity_ids = get_wishlist_entity_ids(user_id, entity_ids)
    for entity_id in wishlist_entity_ids:
        entity_id_wise_wishlist_status[entity_id] = True
    return entity_id_wise_wishlist_status


def get_rating_wise_review_details_for_entity(entity_id):
    from Bookings.exportapi import get_booking_ids_for_entity
    booking_ids = get_booking_ids_for_entity(entity_id)
    return get_rating_stats_for_related_ids(booking_ids)


def get_rating_type_wise_average_rating_for_entity(entity_id):
    from Bookings.exportapi import get_booking_ids_for_entity
    booking_ids = get_booking_ids_for_entity(entity_id)
    return get_rating_type_wise_average_rating_for_related_ids(booking_ids)


def get_latest_ratings_for_entity(entity_id):
    from Bookings.exportapi import get_booking_ids_for_entity
    booking_ids = get_booking_ids_for_entity(entity_id)
    return get_latest_ratings_for_related_ids(booking_ids)
