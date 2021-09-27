import json


def is_json(my_json):
    try:
        json_object = json.loads(my_json)
    except ValueError as e:
        return False
    return True
