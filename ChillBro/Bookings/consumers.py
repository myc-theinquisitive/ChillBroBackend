from .serializers import BookingsSerializer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from djangochannelsrestframework.permissions import IsAuthenticated
from .models import Bookings


class BookingInstanceConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer
    permission_classes = (IsAuthenticated, )
