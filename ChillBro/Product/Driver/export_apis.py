from django.db.models import F


def check_driver_exists(driver_id):
    from .models import Driver
    try:
        Driver.objects.get(product_id=driver_id)
    except:
        return False
    return True


def get_driver_details(driver_id):
    from .views import DriverView
    return DriverView().get(driver_id)


def get_drivers_details(driver_ids):
    from .views import DriverView
    return DriverView().get_by_ids(driver_ids)


def get_basic_driver_details(driver_id):
    from .models import Driver
    return Driver.objects.select_related('product').filter(product_id=driver_id) \
        .values(driver_id=F('product__id'), name=F('product__name')).first()


def get_basic_drivers_details(driver_ids):
    from .models import Driver
    return Driver.objects.select_related('product').filter(product_id__in=driver_ids) \
        .values(driver_id=F('product__id'), name=F('product__name'))
