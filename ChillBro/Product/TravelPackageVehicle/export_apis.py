from django.db.models import Count
from collections import defaultdict
from .models import TravelPackageVehicle


def travel_package_id_wise_vehicles_count(travel_package_ids):
    travel_package_vehicles_count = TravelPackageVehicle.objects.filter(travel_package_id__in=travel_package_ids) \
        .values('travel_package').annotate(count=Count('id')).values('travel_package_id', 'count')

    travel_package_wise_vehicles_count = defaultdict(int)
    for travel_package_vehicle_count in travel_package_vehicles_count:
        travel_package_wise_vehicles_count[travel_package_vehicle_count["travel_package_id"]] = \
            travel_package_vehicle_count["count"]

    return travel_package_wise_vehicles_count
