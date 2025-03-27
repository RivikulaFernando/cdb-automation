import cv2
import os
from datetime import datetime

def capture_image(ip_address, username, password, save_directory):
    """
    Capture an image from the Axis P5522 camera and save it.
    
    Args:
        ip_address (str): The IP address of the camera.
        username (str): The camera username.
        password (str): The camera password.
        save_directory (str): Directory where the image will be saved.
    """
    # Construct video stream URL
    url = f"http://{username}:{password}@{ip_address}/mjpg/video.mjpg"
    
    # Open video capture
    cap = cv2.VideoCapture(url)
    
    if not cap.isOpened():
        print("Error: Unable to connect to the camera")
        return
    
    # Read frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Failed to capture image")
        return
    
    # Ensure save directory exists
    os.makedirs(save_directory, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_directory, f"capture_{timestamp}.jpg")
    
    # Save image
    cv2.imwrite(filename, frame)
    return filename

