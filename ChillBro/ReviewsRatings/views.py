from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ReviewsRatingsSerializer, EntityTotalReviewsSerializer, BCAppFeedbackAndSuggestionsSerializer, \
    GetBCAppFeedbackAndSuggestionsSerializer, EntityReviewStatisticsSerializer, \
    CustomerAppFeedbackAndSuggestionsSerializer, GetCustomerAppFeedbackAndSuggestionsSerializer, \
    CustomerAppRatingSerializer, BCAppRatingSerializer
from .models import ReviewsRatings, BCAppFeedbackAndSuggestions, CustomerAppFeedbackAndSuggestions, CustomerAppRating, \
    BCAppRating
from .helpers import *
from .wrapper import *
from ChillBro.permissions import IsOwner
from django.conf import settings
from rest_framework.views import APIView


class ReviewRatingList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        return super().post(request, args, kwargs)


class EntityReviewRatingList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        if kwargs['entity_id'] == "MYC":
            data = {'related_id': settings.MYC_ID, 'comment': request.data['comment'],
                    'rating': request.data['rating'], 'created_by': request.user}
        else:
            data = {'related_id': kwargs['entity_id'], 'comment': request.data['comment'],
                    'rating': request.data['rating'], 'created_by': request.user}
        serializer = ReviewsRatingsSerializer()
        serializer.create(data)
        return Response({"message": "success"}, 200)

        
class GetBusinessCleintToMYCReview(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        try:
            business_client_review_to_MYC = ReviewsRatings.objects.get(
                related_id="MYC", created_by=request.user)
        except ObjectDoesNotExist:
            return Response({"results": {}}, 200)
        serializer = ReviewsRatingsSerializer(business_client_review_to_MYC)
        return Response({"results": serializer.data}, 200)


class ReviewRatingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

    def put(self, request, *args, **kwargs):
        try:
            review = ReviewsRatings.objects.get(id=kwargs['pk'])
            self.check_object_permissions(request, review)
        except ObjectDoesNotExist:
            pass
        request.data["created_by"] = request.user.id
        return super().put(request, args, kwargs)


class RelatedReviewRatingList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

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

    def post(self, request, *args, **kwargs):
        input_serializer = EntityReviewStatisticsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Cant get review statistics details", "errors": input_serializer.errors}, 400)

        entity_filters = get_entity_type(request.data['entity_filters'])
        entity_ids = request.data['entity_ids']

        bookings = get_completed_bookings_by_entity_id(entity_filters, entity_ids)
        booking_ids = []
        for each_booking in bookings:
            booking_ids.append(each_booking)

        reviews = ReviewsRatings.objects.filter(related_id__in=booking_ids)
        total_reviews = len(reviews)
        if(total_reviews == 0):
            return Response(
                {
                    "total_reviews": 0,
                    "rating_average": 0,
                    "rating_percentage": 0.00},
                200
            )

        rating_average = reviews.aggregate(
            rating_average=Avg('rating'))['rating_average']
        return Response(
            {
                "total_reviews": total_reviews,
                "rating_average": rating_average,
                "rating_percentage": (rating_average/REVIEW_SCALE)*100},
            200
        )


class EntityTotalReviews(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = EntityTotalReviewsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"errors": input_serializer.errors}, 400)

        date_filter = request.data['date_filter']
        entity_filters = get_entity_type(request.data['entity_filters'])
        rating_filters = get_rating_filters(request.data['rating_filters'])
        comment_required = request.data['comment_required']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        entity_ids = request.data['entity_ids']
        bookings = get_completed_bookings_by_entity_id(entity_filters, entity_ids)
        booking_ids = []
        for each_booking in bookings:
            booking_ids.append(each_booking)
        
        if comment_required:
            if date_filter == 'Total':
                reviews = ReviewsRatings.objects\
                .filter(Q(related_id__in=booking_ids) & Q(rating__in=rating_filters))
            else:
                reviews = ReviewsRatings.objects\
                .filter(Q(reviewed_time__gte=from_date) & Q(reviewed_time__lte=to_date) &
                        Q(related_id__in=booking_ids) & Q(rating__in=rating_filters))
        else:
            if date_filter == 'Total':
                reviews = ReviewsRatings.objects\
                .filter(Q(related_id__in=booking_ids) & Q(rating__in=rating_filters))
            else:
                reviews = ReviewsRatings.objects \
                .filter(Q(reviewed_time__gte=from_date) & Q(reviewed_time__lte=to_date) &
                        Q(related_id__in=booking_ids) & Q(rating__in=rating_filters) &
                        Q(Q(comment="") | Q(comment=None)))

        booking_ratings = []
        for each_review in reviews:
            review = {
                'rating': each_review.rating,
                'comment': each_review.comment,
                'booking_id': each_review.related_id,
                'check_out': each_review.reviewed_time,
                'total_money': bookings[str(each_review.related_id)]['total_money']
            }
            booking_ratings.append(review)

        return Response({"results": booking_ratings}, 200)


class CreateBCAppFeedbackAndSuggestion(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        input_serializer = BCAppFeedbackAndSuggestionsSerializer(data=request.data)
        if input_serializer.is_valid():
            input_serializer.save()
            return Response({"message": "Successfully given feedback"}, 200)
        else:
            return Response({"message": "Feedback is not submitted", "errors": input_serializer.errors}, 400)


class GetBCAppFeedbackAndSuggestions(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = GetBCAppFeedbackAndSuggestionsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get the feedback details", "errors": input_serializer.errors}, 400)

        categories = get_bc_app_feedback_categories(request.data['category_filters'])
        feedback = BCAppFeedbackAndSuggestions.objects.filter(category__in=categories)
        serializer = BCAppFeedbackAndSuggestionsSerializer(feedback, many=True)
        return Response({"results": serializer.data}, 200)


class CreateCustomerAppFeedbackAndSuggestion(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        input_serializer = CustomerAppFeedbackAndSuggestionsSerializer(data=request.data)
        if input_serializer.is_valid():
            input_serializer.save()
            return Response({"message": "Successfully given feedback"}, 200)
        else:
            return Response({"message": "Feedback is not submitted", "errors": input_serializer.errors}, 400)


class GetCustomerAppFeedbackAndSuggestions(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = GetCustomerAppFeedbackAndSuggestionsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get the feedback details", "errors": input_serializer.errors}, 400)

        queryset = CustomerAppFeedbackAndSuggestions.objects
        categories = request.data['category_filters']
        if categories:
            queryset = queryset.filter(category__in=categories)
        modules = request.data['module_filters']
        if modules:
            queryset = queryset.filter(module__in=modules)
        serializer = CustomerAppFeedbackAndSuggestionsSerializer(queryset.all(), many=True)
        return Response({"results": serializer.data}, 200)


class CustomerAppRatingList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CustomerAppRating.objects.all().order_by("-submitted_on")
    serializer_class = CustomerAppRatingSerializer

    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        response = super().post(request, args, kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data = {"message": "Feedback Submitted Successfully"}
        return response


class GetCustomerAppLastRatingForUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        last_review = CustomerAppRating.objects.filter(created_by=request.user).order_by("-submitted_on").first()
        if last_review:
            response_data = {
                "rating_given": True,
                "rating": last_review.rating,
                "comment": last_review.comment,
                "submitted_on": last_review.submitted_on
            }
        else:
            response_data = {
                "rating_given": False
            }
        return Response(response_data, status=status.HTTP_200_OK)


class BCAppRatingList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BCAppRating.objects.all().order_by("-submitted_on")
    serializer_class = BCAppRatingSerializer

    def post(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        response = super().post(request, args, kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data = {"message": "Feedback Submitted Successfully"}
        return response


class GetBCAppLastRatingForUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        last_review = BCAppRating.objects.filter(created_by=request.user).order_by("-submitted_on").first()
        if last_review:
            response_data = {
                "rating_given": True,
                "rating": last_review.rating,
                "comment": last_review.comment,
                "submitted_on": last_review.submitted_on
            }
        else:
            response_data = {
                "rating_given": False
            }
        return Response(response_data, status=status.HTTP_200_OK)
