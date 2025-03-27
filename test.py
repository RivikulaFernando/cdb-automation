from vision import detect_car_details
from camera import capture_image


file_path = capture_image("169.254.160.88", "root", "entc", "captures")
print(detect_car_details(file_path))