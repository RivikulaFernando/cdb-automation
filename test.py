from vision import detect_car_details
from camera import AxisP5522Camera


# file_path = capture_image("169.254.40.128", "root", "entc", "captures")
# print(detect_car_details(file_path))
# Initialize the camera
camera = AxisP5522Camera(ip_address="169.254.40.128", username="root", password="entc")

# Capture an image
image_path = camera.capture_image()
print(f"Captured image path: {image_path}")

if image_path:
    # Detect face and get center coordinates
    centers = camera.detect_face(image_path)
    print
    if centers:
        print(f"👤 Detected face centers: {centers}")
        # Move camera to the first detected face
        x, y = centers[0]
        camera.move_and_zoom_camera(x, y, zoom_level=3)