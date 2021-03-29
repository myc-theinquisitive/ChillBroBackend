from django.utils.text import slugify
import uuid
from django.shortcuts import get_object_or_404


def image_upload_to_product(instance, filename):
    name = instance.product.name
    slug = slugify(name)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, str(uuid.uuid4()), file_extension)
    return "static/images/Product/%s/%s" % (slug, new_filename)

def getDepartmentChoices():
    return ((1,"Customer Care"),(2,"Account Section"),(3,"Finance"))

department_choices=getDepartmentChoices()
def getEntityByProductId(product_id):
    return "Hotel_123"

def getUserId():
    return "123"  #get user id from token

class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """

    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]:  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)  # Lookup the object