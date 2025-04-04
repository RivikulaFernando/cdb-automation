import json

# Database of vehicles
vehicle_db = [
    {
        "license_no": "ABC123",
        "type": "Car",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Red",
        "vehicle_number": "V12345",
        "engine_number": "E67890"
    },
    {
        "license_no": "XYZ789",
        "type": "Motorcycle",
        "brand": "Honda",
        "model": "CBR500R",
        "color": "Black",
        "vehicle_number": "V54321",
        "engine_number": "E09876"
    },
    {
        "license_no": "LMN456",
        "type": "Truck",
        "brand": "Ford",
        "model": "F-150",
        "color": "Blue",
        "vehicle_number": "V11223",
        "engine_number": "E33445"
    }
]

# Function to search vehicle details by license number
def get_vehicle_details_by_license(license_no):
    for vehicle in vehicle_db:
        if vehicle["license_no"] == license_no:
            return vehicle
    return None