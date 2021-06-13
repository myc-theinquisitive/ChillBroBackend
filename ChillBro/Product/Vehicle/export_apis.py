def get_vehicle_details(vehicle_id):
    from .views import VehicleView
    return VehicleView().get(vehicle_id)


def get_vehicles_details(vehicle_ids):
    from .views import VehicleView
    return VehicleView().get_by_ids(vehicle_ids)


def check_vehicle_exists(vehicle_id):
    from .models import Vehicle
    try:
        Vehicle.objects.get(product_id=vehicle_id)
    except:
        return False
    return True
