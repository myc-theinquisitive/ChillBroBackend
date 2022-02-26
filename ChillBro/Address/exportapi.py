from .serializers import AddressSerializer
from django.db.models import F
from django.db.models.functions import Abs
from .views import create_address, update_address, get_address_details


def filter_by_city(address_ids, city):
    from .models import Address
    return Address.objects.filter(id__in=address_ids).filter(city=city).values_list("id", flat=True)


def validate_address(address_details):
    valid_serializer = AddressSerializer(data=address_details)
    if valid_serializer.is_valid():
        return True, {}
    else:
        return False, valid_serializer.errors


def approximate_distance_query(address_id, latitude, longitude):
    from .models import Address
    return Address.objects.filter(id=address_id)\
        .annotate(distance=Abs(F('latitude') - latitude) + Abs(F('longitude') - longitude)) \
        .values('distance')
