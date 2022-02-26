from ChillBro.constants import Countries, States, Cities
import enum

DISTANCE_MATRIX_BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
DISTANCE_MATRIX_SINGLE_POINT_URL = DISTANCE_MATRIX_BASE_URL + '&origins={},{}&destinations={},{}&key={}'
DISTANCE_MATRIX_MULTI_POINT_URL = DISTANCE_MATRIX_BASE_URL + '&origins={},{}&destinations={}&key={}'


class AddressType(enum.Enum):
    HOME = "HOME"
    WORK = "WORK"
