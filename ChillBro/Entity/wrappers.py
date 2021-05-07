from Address import exportapi

def create_address(city,pincode):
    return exportapi.create_address({'city':city, 'pincode':pincode})
