from Product.product_interface import ProductInterface
from .serializers import MakeYourOwnTripSerializer, MakeYourOwnTripPlacesSerializer
from typing import Dict
from collections import defaultdict
from .models import MakeYourOwnTrip, MakeYourOwnTripPlaces
from .wrapper import get_place_id_wise_details


class MakeYourOwnTripView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.make_your_own_trip_serializer = None
        self.make_your_own_trip_object = None

        self.places_data = {}

    # initialize the instance variables before accessing
    def initialize_product_class(self, make_your_own_trip_data):

        make_your_own_trip_object_defined = self.make_your_own_trip_object is not None
        make_your_own_trip_data_defined = make_your_own_trip_data is not None

        if make_your_own_trip_data_defined:
            if "places" in make_your_own_trip_data:
                self.places_data = make_your_own_trip_data.pop("places", [])

        # for update
        if make_your_own_trip_object_defined and make_your_own_trip_data_defined:
            self.make_your_own_trip_serializer = MakeYourOwnTripSerializer(self.make_your_own_trip_object,
                                                                           data=make_your_own_trip_data)
        # for create
        elif make_your_own_trip_data_defined:
            self.make_your_own_trip_serializer = MakeYourOwnTripSerializer(data=make_your_own_trip_data)
        # for get
        elif make_your_own_trip_object_defined:
            self.make_your_own_trip_serializer = MakeYourOwnTripSerializer(self.make_your_own_trip_object)
        else:
            self.make_your_own_trip_serializer = MakeYourOwnTripSerializer()

    def validate_create_data(self, make_your_own_trip_data: Dict) -> (bool, Dict):
        print(make_your_own_trip_data, 'inside data of make my trip')

        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(make_your_own_trip_data)

        make_your_own_trip_data_valid = self.make_your_own_trip_serializer.is_valid()
        if not make_your_own_trip_data_valid:
            is_valid = False
            errors.update(self.make_your_own_trip_serializer.errors)

        # Validating places
        make_your_own_trip_places_serializer = MakeYourOwnTripPlacesSerializer(data=self.places_data, many=True)
        if not make_your_own_trip_places_serializer.is_valid():
            is_valid = False
            errors["places"] = make_your_own_trip_places_serializer.errors

        return is_valid, errors

    def create(self, make_your_own_trip_data):
        """
        make_your_own_trip: {
            "product_id": string, # internal data need not be validated
            "created_by" : string
            "places": {
                place: string
            }
        }
        """

        make_your_own_trip_object = self.make_your_own_trip_serializer.create(make_your_own_trip_data)

        # Add Places to Make Your Own Trip
        for place_dict in self.places_data:
            place_dict["make_your_own_trip"] = make_your_own_trip_object.id
        MakeYourOwnTripPlacesSerializer.bulk_create(self.places_data)

        return {
            "id": make_your_own_trip_object.id
        }

    def validate_update_data(self, make_your_own_trip_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.make_your_own_trip_object \
                = MakeYourOwnTrip.objects.get(product_id=make_your_own_trip_data["product"])
        except MakeYourOwnTrip.DoesNotExist:
            return False, {"errors": "MakeYourOwnTrip does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(make_your_own_trip_data)

        make_your_own_trip_data_valid = self.make_your_own_trip_serializer.is_valid()
        if not make_your_own_trip_data_valid:
            is_valid = False
            errors.update(self.make_your_own_trip_serializer.errors)
        
        # validate places for travel agency
        if self.places_data:
            if "add" in self.places_data:
                place_ids = []
                for make_your_own_trip_place in self.places_data["add"]:
                    place_ids.append(make_your_own_trip_place["place"])

                # TODO: validate place ids
                # invalid_product_ids = get_invalid_product_ids(product_ids)
                invalid_place_ids = []
                if len(invalid_place_ids) != 0:
                    is_valid = False
                    errors["places"].append("Some of the places are not valid")

        return is_valid, errors

    def update(self, make_your_own_trip_data):
        """
        make_your_own_trip: {
            "product_id": string, # internal data need not be validated
            "places":[
                "add":[ ]
                "delete":[ ]
            ]
        }
        """

        self.make_your_own_trip_serializer.update(self.make_your_own_trip_object, make_your_own_trip_data)
        # Add Places to Make Your Own Trip
        make_your_own_trip_places_add_dicts = []
        if "add" in self.places_data:
            for place_dict in self.places_data["add"]:
                make_your_own_trip_place_dict = {
                    "make_your_own_trip": self.make_your_own_trip_object.id,
                    "place": place_dict["place"],
                }
                make_your_own_trip_places_add_dicts.append(make_your_own_trip_place_dict)
            MakeYourOwnTripPlacesSerializer.bulk_create(make_your_own_trip_places_add_dicts)

        # Deleting Places for Make Your Own Trip
        if "delete" in self.places_data:
            delete_places = self.places_data["delete"]
            MakeYourOwnTripPlacesSerializer.bulk_delete(self.make_your_own_trip_object.id, delete_places)

    @staticmethod
    def get_make_your_own_trip_id_wise_places_details(make_your_own_trip_ids):
        make_your_own_trip_places = MakeYourOwnTripPlaces.objects.filter(make_your_own_trip_id__in=make_your_own_trip_ids)

        place_ids = []
        for make_your_own_trip_place in make_your_own_trip_places:
            place_ids.append(make_your_own_trip_place.place_id)

        place_id_wise_details = get_place_id_wise_details(place_ids)

        make_your_own_trip_id_wise_places = defaultdict(list)
        for make_your_own_trip_place in make_your_own_trip_places:
            make_your_own_trip_id_wise_places[make_your_own_trip_place.make_your_own_trip_id].append(
                {
                    "place": place_id_wise_details[make_your_own_trip_place.place_id],
                }
            )

        return make_your_own_trip_id_wise_places

    def get(self, product_id):
        self.make_your_own_trip_object = MakeYourOwnTrip.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        make_your_own_trip_data = self.make_your_own_trip_serializer.data

        make_your_own_trip_id_wise_places = self.get_make_your_own_trip_id_wise_places_details([self.make_your_own_trip_object.id])

        places = make_your_own_trip_id_wise_places[self.make_your_own_trip_object.id]
        make_your_own_trip_data["places"] = places


        return make_your_own_trip_data

    def get_by_ids(self, product_ids):
        make_your_own_trips = MakeYourOwnTrip.objects.filter(product_id__in=product_ids)

        make_your_own_trip_serializer = MakeYourOwnTripSerializer(make_your_own_trips, many=True)
        make_your_own_trips_data = make_your_own_trip_serializer.data

        make_your_own_trip_ids = MakeYourOwnTrip.objects.filter(product_id__in=product_ids).values_list('id')
        make_your_own_trip_id_wise_places = self.get_make_your_own_trip_id_wise_places_details(make_your_own_trip_ids)

        for make_your_own_trip_data in make_your_own_trips_data:
            make_your_own_trip_data['places'] = make_your_own_trip_id_wise_places[make_your_own_trip_data["id"]]


        return make_your_own_trips_data
