def get_vehicle_details(vehicle_id):
    from .views import VehicleView
    return VehicleView().get(vehicle_id)


def get_vehicles_details(vehicle_ids):
    from .views import VehicleView
    return VehicleView().get_by_ids(vehicle_ids)
