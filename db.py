import json

# Database of vehicles
vehicle_db = [
    {
        "license_no": "KM-5141",
        "type": "Car",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Silver",
        "engine_number": "3ZZ-40760431598",
        "chassis_number": "ZZE121-8003692"
    },
    {
        "license_no": "KL-1234",
        "type": "Bike",
        "brand": "Honda",
        "model": "CBR500R",
        "color": "Red",
        "engine_number": "CBR500R-1234567890",
        "chassis_number": "CBR500R-0987654321"
    },
    {
        "license_no": "KA-5678",
        "type": "Truck",
        "brand": "Ford",
        "model": "F-150",
        "color": "Blue",
        "engine_number": "F150-9876543210",
        "chassis_number": "F150-1234567890"
    }

]

# Function to search vehicle details by license number


def get_vehicle_details_by_license(license_no):
    for vehicle in vehicle_db:
        if vehicle["license_no"] == license_no:
            return vehicle
    return None
