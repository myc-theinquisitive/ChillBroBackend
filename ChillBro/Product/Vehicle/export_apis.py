def get_vehicle_type_details(vehicle_type_id):
    from .views import VehicleTypeView
    return VehicleTypeView().get(vehicle_type_id)


def get_vehicle_types_details(vehicle_type_ids):
    from .views import VehicleTypeView
    return VehicleTypeView().get_by_ids(vehicle_type_ids)
