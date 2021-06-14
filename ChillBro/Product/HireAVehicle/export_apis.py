def get_hire_a_vehicle_details(hire_a_vehicle_ids):
    from .views import HireAVehicleView
    return HireAVehicleView().get_sub_products_ids(hire_a_vehicle_ids)