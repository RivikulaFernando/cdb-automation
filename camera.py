import cv2
import os
from datetime import datetime
import requests

class AxisP5522Camera:
    def __init__(self, ip_address, username, password, save_directory="captures"):
        """
        Initialize the Axis P5522 Camera controller.

        Args:
            ip_address (str): The IP address of the camera.
            username (str): The camera username.
            password (str): The camera password.
            save_directory (str, optional): Directory where images will be saved. Defaults to "Camera_Captures".
        """
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.save_directory = save_directory

    def capture_image(self):
        """
        Captures an image from the camera and saves it in the save directory.
        """
        url = f"http://{self.username}:{self.password}@{self.ip_address}/mjpg/video.mjpg"
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            print("Error: Unable to connect to the camera")
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("Error: Failed to capture image")
            return None
        
        os.makedirs(self.save_directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_directory, f"capture_{timestamp}.jpg")
        
        cv2.imwrite(filename, frame)
        print(f"✅ Image saved at: {filename}")
        return filename

    
