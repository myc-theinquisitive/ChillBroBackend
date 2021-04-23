from django.db.models import Avg
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import ReviewsRatingsSerializer
from .models import ReviewsRatings


class ReviewRatingList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

    def post(self, request, *args, **kwargs):
        request.data["reviewed_by"] = request.user.id
        return super().post(request, args, kwargs)


class ReviewRatingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReviewsRatings.objects.all()
    serializer_class = ReviewsRatingsSerializer

    def put(self, request, *args, **kwargs):
        request.data["reviewed_by"] = request.user.id
        return super().put( request, args, kwargs)


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
            'overall_rating' : overall_rating['rating__avg'],
            'reviews' : response.data
        }
        response.data = response_data
        return response


