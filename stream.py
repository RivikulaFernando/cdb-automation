import cv2
import numpy as np
import os
from datetime import datetime

# YOLO Model Files
yolo_config = "models/yolov4/yolov4-tiny.cfg"
yolo_weights = "models/yolov4/yolov4-tiny.weights"
yolo_classes = "models/yolov4/coco.names"

# Load YOLO
net = cv2.dnn.readNet(yolo_weights, yolo_config)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load class names
with open(yolo_classes, "r") as f:
    classes = f.read().strip().split("\n")

# Car-related classes in COCO
vehicle_classes = {"car": 2, "bus": 5, "truck": 7}

def connect_camera(ip_address, username="root", password="entc", save_directory=None):
    """ Connects to the camera and starts vehicle detection. """
    url = f"http://{username}:{password}@{ip_address}/mjpg/video.mjpg"
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print("❌ Unable to connect to the camera")
        return

    if save_directory is None:
        save_directory = 'captures'
    os.makedirs(save_directory, exist_ok=True)

    detect_vehicles(cap, save_directory)

def detect_vehicles(cap, save_directory):
    """ Continuously detects vehicles and captures only one image per appearance. """
    vehicle_present = False  # Tracks if a vehicle is currently in frame
    image_captured = False  # Ensures only one image is saved per detection

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width = frame.shape[:2]

        # YOLO Preprocessing
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward(output_layers)

        vehicle_detected = False

        for detection in detections:
            for obj in detection:
                scores = obj[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.7 and class_id in vehicle_classes.values():
                    vehicle_detected = True
                    label = classes[class_id]

                    # Bounding Box
                    center_x, center_y, w, h = (obj[0:4] * np.array([width, height, width, height])).astype("int")
                    x, y = int(center_x - w / 2), int(center_y - h / 2)

                    # Draw Detection
                    color = (0, 255, 0)  # Green
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Capture Only One Image When a New Vehicle Appears
        if vehicle_detected and not vehicle_present:
            print("🚗 Vehicle detected! Capturing image...")
            vehicle_present = True
            image_captured = False  # Reset for next detection

        if vehicle_present and not image_captured:
            capture_image(frame, save_directory)
            image_captured = True  # Prevent multiple captures

        if not vehicle_detected and vehicle_present:
            print("🚘 Vehicle left! Resetting detection...")
            vehicle_present = False  # Reset for the next vehicle
            image_captured = False  # Allow new captures

        cv2.imshow("Camera Feed", frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Monitoring Stopped.")

def capture_image(frame, save_directory):
    """ Saves a single image of the detected vehicle. """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_directory, f"vehicle_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    print(f"📸 Image saved: {filename}")

if __name__ == "__main__":
    ip_address = "169.254.40.128"  # Change to your IP camera's address
    connect_camera(ip_address)
