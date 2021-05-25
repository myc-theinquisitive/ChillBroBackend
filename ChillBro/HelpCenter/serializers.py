from rest_framework import serializers
from .models import Carousel, CarouselItem, BusinessClientFAQ, HowToUse, HelpCenterFAQ
from django.conf import settings


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'

class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = '__all__'
        
    def to_representation(self, data):
        data = super(CarouselItemSerializer, self).to_representation(data)
        data['image'] = data.get('image').replace(settings.IMAGE_REPLACED_STRING, '')
        return data

class BusinessClientFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientFAQ
        fields = '__all__'

class HelpCenterFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpCenterFAQ
        fields = '__all__'

class HowToUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowToUse
        fields = '__all__'