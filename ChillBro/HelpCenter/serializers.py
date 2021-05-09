from rest_framework import serializers
from .models import Carousel, CarouselItem, BusinessClientFAQ, HowToUse


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'

class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = '__all__'

class BusinessClientFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientFAQ
        fields = '__all__'

class HowToUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowToUse
        fields = '__all__'