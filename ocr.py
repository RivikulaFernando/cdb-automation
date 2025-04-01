import easyocr
import cv2
import numpy as np
import re

reader = easyocr.Reader(["en"])


def recognize_license_plate(image_path, x, y, w, h, padding_x=15, padding_y=10):
    """Crops the license plate from the image, preprocesses it, extracts the text, and plots the detection."""
    # Load image
    image = cv2.imread(image_path)

    # Calculate coordinates with padding
    x_min, y_min = max(0, int(x - w / 2) - padding_x), max(0,
                                                           int(y - h / 2) - padding_y)
    x_max, y_max = min(image.shape[1], int(
        x + w / 2) + padding_x), min(image.shape[0], int(y + h / 2) + padding_y)

    # Extract the license plate area
    license_plate_img = image[y_min:y_max, x_min:x_max]

    # Convert to grayscale and apply adaptive threshold
    gray_plate = cv2.cvtColor(license_plate_img, cv2.COLOR_BGR2GRAY)
    gray_plate = cv2.adaptiveThreshold(
        gray_plate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Try different scales for better recognition
    plate_number = ""
    for scale in [1.0, 1.5, 2]:
        resized = cv2.resize(gray_plate, None, fx=scale,
                             fy=scale, interpolation=cv2.INTER_CUBIC)
        result_text = reader.readtext(resized, detail=0)
        if result_text:
            plate_number = " ".join(result_text)
            break

    # Clean and format the plate number
    plate_number = plate_number.upper()
    # Remove unwanted characters
    plate_number = re.sub(r"[^A-Z0-9 ]", "", plate_number)
    plate_number = re.sub(r"\s+", " ", plate_number).strip()  # Fix spaces

    plate_number_list = plate_number.split()
    plate_number = "-".join(plate_number_list[-2:])

    # If the result seems invalid, return "NOT DETECTED"
    if len(plate_number) < 7 or not any(char.isdigit() for char in plate_number):
        plate_number = "NOT DETECTED"

    return plate_number
