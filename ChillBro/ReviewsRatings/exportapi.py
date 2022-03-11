from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count, Q, Subquery, F, OuterRef
from .constants import BASE_RATING_STRING, BUSINESS_CLIENT_REVIEW_ON_CUSTOMER, REVIEW_SCALE
from .serializers import *


def insert_business_client_review_for_customer(validated_data):
    validated_data["rating_type"] = BUSINESS_CLIENT_REVIEW_ON_CUSTOMER
    rating_serializer = ReviewsRatingsSerializer()
    return rating_serializer.create(validated_data)


def business_client_review_for_customer_by_booking_id(booking_id):
    try:
        review = ReviewsRatings.objects.get(related_id=booking_id, rating_type=BUSINESS_CLIENT_REVIEW_ON_CUSTOMER)
    except ObjectDoesNotExist:
        return {}
    return CustomerReviewSerializer(review).data


def average_rating_query_for_related_ids(related_ids):
    return ReviewsRatings.objects.filter(related_id__in=related_ids, rating_type=BASE_RATING_STRING)\
        .values('rating_type').annotate(avg_rating=Avg('rating')).values('avg_rating')


def total_reviews_query_for_related_ids(related_ids):
    return ReviewsRatings.objects.filter(related_id__in=related_ids, rating_type=BASE_RATING_STRING)\
        .values('rating_type').annotate(total_reviews=Count('id')).values('total_reviews')


def average_rating_query_for_related_id(related_id):
    return ReviewsRatings.objects.filter(related_id=related_id,
                                         rating_type=BASE_RATING_STRING).values('rating')\
                .annotate(avg_rating=Avg('rating')).values('avg_rating')


def average_rating_query_for_secondary_related_id(secondary_related_id):
    return ReviewsRatings.objects.filter(secondary_related_id=secondary_related_id,
                                         rating_type=BASE_RATING_STRING).values('rating')\
                .annotate(avg_rating=Avg('rating')).values('avg_rating')


def get_related_id_wise_average_rating(related_ids):
    return ReviewsRatings.objects.filter(related_id__in=related_ids,
                                         rating_type=BASE_RATING_STRING) \
        .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))\
        .values('avg_rating', 'related_id', 'total_reviews')


def get_secondary_related_id_wise_average_rating(secondary_related_ids):
    return ReviewsRatings.objects.filter(secondary_related_id__in=secondary_related_ids,
                                         rating_type=BASE_RATING_STRING) \
        .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))\
        .values('avg_rating', 'secondary_related_id', 'total_reviews')


def get_rating_stats_for_secondary_related_id(secondary_related_id):
    ratings_count = ReviewsRatings.objects.filter(secondary_related_id=secondary_related_id,
                                                  rating_type=BASE_RATING_STRING)\
        .values('rating').annotate(count=Count('id'))

    rating_wise_count = defaultdict(int)
    total_count = 0
    for rating_count in ratings_count:
        rating_wise_count[rating_count["rating"]] = rating_count["count"]
        total_count += rating_count["count"]

    rating_stats = []
    for rating in range(REVIEW_SCALE, 0, -1):
        if total_count == 0:
            percentage = 0
        else:
            percentage = (rating_wise_count[rating] / total_count) * 100
        rating_stat_dict = {
            "rating": rating,
            "count": rating_wise_count[rating],
            "percentage": percentage
        }
        rating_stats.append(rating_stat_dict)
    return rating_stats


def get_rating_type_wise_average_rating_for_secondary_related_id(secondary_related_id):
    exclude_rating_types = [BUSINESS_CLIENT_REVIEW_ON_CUSTOMER]
    return ReviewsRatings.objects.filter(secondary_related_id=secondary_related_id)\
        .filter(~Q(rating_type__in=exclude_rating_types))\
        .values('rating_type').annotate(avg_rating=Avg('rating'), total_reviews=Count('rating'))


def get_latest_ratings_for_secondary_related_id(secondary_related_id):
    reviews = ReviewsRatings.objects.select_related('created_by').filter(
        secondary_related_id=secondary_related_id, rating_type=BASE_RATING_STRING).order_by('-reviewed_time')[:10]

    ratings = []
    for review in reviews:
        review_dict = {
            "rating": review.rating,
            "comment": review.comment,
            "reviewed_time": review.reviewed_time,
            "user": {
                "name": review.created_by.first_name + review.created_by.last_name
            }
        }
        ratings.append(review_dict)

    return ratings


def get_rating_stats_for_related_ids(related_ids):
    ratings_count = ReviewsRatings.objects.filter(related_id__in=related_ids,
                                                  rating_type=BASE_RATING_STRING)\
        .values('rating').annotate(count=Count('id'))

    rating_wise_count = defaultdict(int)
    total_count = 0
    for rating_count in ratings_count:
        rating_wise_count[rating_count["rating"]] = rating_count["count"]
        total_count += rating_count["count"]

    rating_stats = []
    for rating in range(REVIEW_SCALE, 0, -1):
        if total_count == 0:
            percentage = 0
        else:
            percentage = (rating_wise_count[rating] / total_count) * 100
        rating_stat_dict = {
            "rating": rating,
            "count": rating_wise_count[rating],
            "percentage": percentage
        }
        rating_stats.append(rating_stat_dict)
    return rating_stats


def get_rating_type_wise_average_rating_for_related_ids(related_ids):
    exclude_rating_types = [BUSINESS_CLIENT_REVIEW_ON_CUSTOMER]
    return ReviewsRatings.objects.filter(related_id__in=related_ids)\
        .filter(~Q(rating_type__in=exclude_rating_types))\
        .values('rating_type').annotate(avg_rating=Avg('rating'), total_reviews=Count('rating'))


# TODO: Check where is it getting used and why
def get_latest_ratings_for_related_ids(related_ids):
    reviews = ReviewsRatings.objects.select_related('created_by').filter(
        related_id__in=related_ids, rating_type=BASE_RATING_STRING).order_by('-reviewed_time')[:10]

    ratings = []
    for review in reviews:
        review_dict = {
            "rating": review.rating,
            "comment": review.comment,
            "reviewed_time": review.reviewed_time,
            "user": {
                "name": review.created_by.first_name + review.created_by.last_name
            }
        }
        ratings.append(review_dict)

    return ratings


def rating_and_comment_for_related_ids(related_ids):
    return ReviewsRatings.objects.filter(
        related_id__in=related_ids, rating_type=BASE_RATING_STRING)\
        .filter(Q(secondary_related_id=None) | Q(secondary_related_id=""))\
        .order_by('reviewed_time').values('related_id', 'rating', 'comment')


def rating_and_comment_for_related_ids_and_secondary_related_ids(related_ids, secondary_related_ids):
    return ReviewsRatings.objects.filter(
        related_id__in=related_ids, secondary_related_id__in=secondary_related_ids,
        rating_type=BASE_RATING_STRING)\
        .order_by('reviewed_time').values('related_id', 'secondary_related_id', 'rating', 'comment')
