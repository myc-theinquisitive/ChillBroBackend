from rest_framework import serializers

from .models import ReviewsRatings


class ReviewsRatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewsRatings
        fields = '__all__'

    def create(self, validated_data):
        object = ReviewsRatings(
            related_id = validated_data['related_id'],
            comment = validated_data['comment'],
            rating=validated_data['rating'],
            reviewed_by = validated_data['reviewed_by']
        )
        return object.save()