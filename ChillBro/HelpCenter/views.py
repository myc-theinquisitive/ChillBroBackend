from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Carousel, CarouselItem, BusinessClientFAQ, HowToUse
from .serializers import CarouselSerializer, CarouselItemSerializer, BusinessClientFAQSerializer, HowToUseSerializer
from datetime import datetime
from django.db.models import Q
from .constants import CarouselItemStatus

class CarouselList(generics.ListCreateAPIView):
    serializer_class = CarouselSerializer
    queryset = Carousel.objects.all()


class CarouselDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CarouselSerializer
    queryset = Carousel.objects.all()


class CarouselItemCreate(generics.CreateAPIView):
    serializer_class = CarouselItemSerializer
    queryset = CarouselItem.objects.all()


class CarouselItemDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CarouselItemSerializer
    queryset = CarouselItem.objects.all()


class CarouselItemToggle(APIView):

    def put(self, request, status):
        if 'id' not in request.data:
            return Response({'error': 'id is required'}, 400)
        id = request.data['id']
        try:
            CarouselItem.objects.filter(id=id).update(status=status)
        except Exception as e:
            print(e)
            return Response({'error': 'Detail not found'}, 400)
        return Response({'message': 'Updated '}, 200)

class CarouselItemsList(generics.ListAPIView):
    serializer_class = CarouselItemSerializer
    queryset = CarouselItem.objects.all()

    def get(self, request, *args, **kwargs):
        carousel_id = self.kwargs['pk']
        current_time = datetime.now()
        self.queryset = CarouselItem.objects.filter(carousel=carousel_id,status=CarouselItemStatus.ACTIVE.value,start__lte=current_time,end__gte=current_time)
        return super().get(request, *args, **kwargs)


class BusinessClientFAQList(generics.ListCreateAPIView):
    serializer_class = BusinessClientFAQSerializer
    queryset = BusinessClientFAQ.objects.all()


class BusinessClientFAQDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessClientFAQSerializer
    queryset = BusinessClientFAQ.objects.all()

class HowToUseList(generics.ListCreateAPIView):
    serializer_class = HowToUseSerializer
    queryset = HowToUse.objects.all()


class HowToUseDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HowToUseSerializer
    queryset = HowToUse.objects.all()

class HowToUseEntityList(generics.ListAPIView):
    serializer_class = HowToUseSerializer
    queryset = HowToUse.objects.all()

    def get(self, request, *args, **kwargs):
        entity_type = self.kwargs['type']
        self.queryset = HowToUse.objects.filter(entity_type=entity_type)
        return super().get(request, *args, **kwargs)