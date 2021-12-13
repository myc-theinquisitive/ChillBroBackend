def get_travel_package_details(travel_package_id, start_time):
    from .views import TravelPackageView
    return TravelPackageView().get(travel_package_id, start_time)
    

def get_travel_package_details_by_ids(travel_package_ids):
    from .views import TravelPackageView
    return TravelPackageView().get_by_ids(travel_package_ids)
    