# import pytest
# from .views import create_booking, cancel_booking, product_availability
#
#
# @pytest.mark.django_db
# def test_booking_creation():
#     # two products available with no previous bookings
#     booking_id = "1"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     # two products available with one previous booking
#     booking_id = "2"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     # two products available with two previous bookings
#     booking_id = "3"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 400
#     assert response.data["message"] == "Booking Not Allowed"
#
#
# @pytest.mark.django_db
# def test_booking_creation_with_equal_start_time_or_end_time():
#     # one products available with no previous bookings
#     booking_id = "1"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     # one products available with one previous bookings and start time equal to previous end time
#     booking_id = "2"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T01:00:00"
#     end_time = "2021-01-01T02:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     # one products available with one previous booking with same start time and end time
#     booking_id = "3"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 400
#     assert response.data["message"] == "Booking Not Allowed"
#
#     # one products available with one previous bookings and start time equal to previous start time
#     booking_id = "4"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T02:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 400
#     assert response.data["message"] == "Booking Not Allowed"
#
#     # one products available with one previous bookings and end time equal to previous end time
#     booking_id = "5"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:30:00"
#     end_time = "2021-01-01T02:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 400
#     assert response.data["message"] == "Booking Not Allowed"
#
#     # one products available with one previous bookings, start time and end time in between previous booking
#     booking_id = "6"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:30:00"
#     end_time = "2021-01-01T00:45:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 400
#     assert response.data["message"] == "Booking Not Allowed"
#
#
# @pytest.mark.django_db
# def test_booking_creation_with_different_product():
#     booking_id = "1"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     # one products available with same time booking for different product
#     booking_id = "2"
#     product_id = "2"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#
# @pytest.mark.django_db
# def test_booking_creation_with_cancelled_booking():
#     booking_id = "1"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     response = cancel_booking(booking_id, product_id)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Cancelled"
#
#     # one product available and one previous booking cancelled with in the booking time
#     booking_id = "2"
#     product_id = "1"
#     product_quantity = 1
#     start_time = "2021-01-01T00:30:00"
#     end_time = "2021-01-01T01:30:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#
# @pytest.mark.django_db
# def test_product_availability():
#     booking_id = "1"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     booking_id = "2"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T01:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T02:00:00"
#
#     response = product_availability(product_id, product_quantity, start_time, end_time)
#     expected_response = {
#         'availabilities': [
#             {'start_hour': '2021-01-01T00:00:00', 'end_hour': '2021-01-01T01:00:00', 'available_count': 0},
#             {'start_hour': '2021-01-01T01:00:00', 'end_hour': '2021-01-01T02:00:00', 'available_count': 2}
#         ]
#     }
#     assert all([a == b for a, b in zip(response.data["availabilities"], expected_response["availabilities"])])
#
#     booking_id = "3"
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T01:00:00"
#     end_time = "2021-01-01T05:00:00"
#
#     response = create_booking(booking_id, product_id, product_quantity, start_time, end_time)
#     assert response.status_code == 200
#     assert response.data["message"] == "Booking Created"
#
#     product_id = "1"
#     product_quantity = 2
#     start_time = "2021-01-01T00:00:00"
#     end_time = "2021-01-01T06:00:00"
#
#     response = product_availability(product_id, product_quantity, start_time, end_time)
#     expected_response = {
#         'availabilities': [
#             {'start_hour': '2021-01-01T00:00:00', 'end_hour': '2021-01-01T01:00:00', 'available_count': 0},
#             {'start_hour': '2021-01-01T01:00:00', 'end_hour': '2021-01-01T02:00:00', 'available_count': 1},
#             {'start_hour': '2021-01-01T02:00:00', 'end_hour': '2021-01-01T03:00:00', 'available_count': 1},
#             {'start_hour': '2021-01-01T03:00:00', 'end_hour': '2021-01-01T04:00:00', 'available_count': 1},
#             {'start_hour': '2021-01-01T04:00:00', 'end_hour': '2021-01-01T05:00:00', 'available_count': 1},
#             {'start_hour': '2021-01-01T05:00:00', 'end_hour': '2021-01-01T06:00:00', 'available_count': 2}
#         ]
#     }
#     assert all([a == b for a, b in zip(response.data["availabilities"], expected_response["availabilities"])])
