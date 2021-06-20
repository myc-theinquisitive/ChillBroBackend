from django.db import models
from .helpers import get_user_model


class MakeYourOwnTrip(models.Model):
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class MakeYourOwnTripPlaces(models.Model):
    make_your_own_trip = models.ForeignKey("MakeYourOwnTrip", on_delete=models.CASCADE,
                                           verbose_name="Make Your Own Trip")
    place = models.ForeignKey("Place", on_delete=models.CASCADE, verbose_name="Make Your Own Trip Place")

    class Meta:
        unique_together = ('make_your_own_trip', 'place',)

    def __str__(self):
        return "Make Your Own Trip Place - {0}, {1}".format(self.make_your_own_trip.product.name, self.place.name)
