from django.db.models import Avg
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ReviewsRatingsSerializer, EntityTotalReviewsSerializer
from .models import ReviewsRatings
from ChillBro.permissions import IsReviewOwner
from .helpers import *
from .wrapper import *

class ReviewRatingList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

    def post(self, request, *args, **kwargs):
        request.data["reviewed_by"] = request.user.id
        return super().post(request, args, kwargs)


class MYCReviewRatingList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = {'related_id': kwargs['entity_id'], 'comment':"", 'rating':request.data['rating'], 'reviewed_by': request.user}
        serializer = ReviewsRatingsSerializer()
        serializer.create(data)
        return Response({"message":"suceess"},200)


class ReviewRatingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsReviewOwner)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer
# pass user object.
    def put(self, request, *args, **kwargs):
        try:
            review=ReviewsRatings.objects.get(id=kwargs['pk'])
            self.check_object_permissions(request,review)
        except:
            pass
        request.data["reviewed_by"] = request.user.id
        return super().put( request, args, kwargs)


class RelatedReviewRatingList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer
# did'nt understand
    def get(self, request, *args, **kwargs):
        related_id = kwargs['related_id']
        self.queryset = ReviewsRatings.objects.filter(related_id=related_id)
        response = super().get(request, args, kwargs)
        overall_rating = ReviewsRatings.objects.filter(related_id=related_id).aggregate(Avg('rating'))
        response_data = {
            'overall_rating': overall_rating['rating__avg'],
            'reviews': response.data
        }
        response.data = response_data
        return response


class EntityReviewStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        reviews = ReviewsRatings.objects.filter(related_id=kwargs['entity_id'])
        total_reviews = len(reviews)
        rating_average =  reviews.aggregate(rating_average = Avg('rating'))['rating_average']
        return Response({"total_reviews":total_reviews,
                         "rating_average":rating_average,
                         "rating_percentage":(rating_average/5)*100},200)


class EntityTotalReviews(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = EntityTotalReviewsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filters = getEntityType(request.data['category_filters'])
            rating_filters = request.data['rating_filters']
            comment_required = request.data['comment_required']
            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            entity_id = kwargs['entity_id']
            bookings = getCompletedBookingsByEntityId(from_date, to_date, entity_filters, entity_id)
            booking_ids = []
            for each_booking in bookings:
                booking_ids.append(each_booking)
            reviews = ReviewsRatings.objects.filter(related_id__in=booking_ids, rating__in = rating_filters)
            booking_ratings = []
            for each_review in reviews:
                review = {'rating': each_review.rating}
                if comment_required:
                    review['comment'] = each_review.comment
                review['booking_id'] = each_review.related_id
                review['check_out'] = bookings[str(each_review.related_id)]['check_out']
                review['total_money'] = bookings[str(each_review.related_id)]['total_money']
                booking_ratings.append(review)
            return Response(booking_ratings, 200)
        else:
            return Response(input_serializer.errors, 400)


