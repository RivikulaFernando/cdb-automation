import asyncio
import os
import shutil
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
# from ocr import recognize_license_plate
from vision import detect_number_plate_vlm, identify_vehicle_details,get_verification_numbers
from db import get_vehicle_details_by_license
from camera import AxisP5522Camera
from fastapi import UploadFile, File

app = FastAPI()

# Directory for storing captured images (keeping them in the same location)
CAPTURED_IMAGES_DIR = "captures"
os.makedirs(CAPTURED_IMAGES_DIR, exist_ok=True)

# Mount the static folder to serve images (keep the original directory)
app.mount("/static", StaticFiles(directory=CAPTURED_IMAGES_DIR), name="static")

license_plate = ""  # Stores the last detected plate
vehicle_details = {}  # Stores the last detected vehicle details
engine_number = ""  # Stores the last detected engine number
chassis_number = ""  # Stores the last detected chassis number
captured_image_path = ""  # Stores the last captured image path
verified = False

camera = AxisP5522Camera(ip_address="192.168.1.135", username="root", password="entc")

# 🌐 Web Interface with live license plate and vehicle details view
@app.get("/debug")
async def get_interface():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Live License Plate & Vehicle Details</title>
        </head>
        <body>
            <h1>Detected Plate: <span id="live-plate">...</span></h1>
            <h2>Vehicle Details:</h2>
            <pre id="vehicle-details">...</pre>
            <h2>Verified:</h2>
            <pre id="verified">...</pre>
            <h2>Captured Image:</h2>
            <img id="captured-image" src="" width="400"/>
            <br>
            <button onclick="capture()">Capture</button>
            <script>
                const wsPlate = new WebSocket(`wss://${location.host}/get_plate`);
                wsPlate.onmessage = function(event) {
                    document.getElementById("live-plate").textContent = event.data;
                };

                const wsDetails = new WebSocket(`wss://${location.host}/get_vehicle_details`);
                wsDetails.onmessage = function(event) {
                    document.getElementById("vehicle-details").textContent = event.data;
                };

                const wsVerified = new WebSocket(`wss://${location.host}/get_verified`);
                wsVerified.onmessage = function(event) {
                    document.getElementById("verified").textContent = event.data;
                };

                const wsImage = new WebSocket(`wss://${location.host}/get_captured_image`);
                wsImage.onmessage = function(event) {
                    document.getElementById("captured-image").src = event.data;
                };

                function capture() {
                    fetch("/capture")
                      .then(res => res.json())
                      .then(data => console.log("Captured:", data));
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 📡 WebSocket endpoint to stream live license plate
@app.websocket("/get_plate")
async def websocket_plate(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(str(license_plate))
        await asyncio.sleep(1)

# 📡 WebSocket endpoint to stream vehicle details
@app.websocket("/get_vehicle_details")
async def websocket_vehicle_details(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "vehicle_details": vehicle_details,
            "engine_number": engine_number,
            "chassis_number": chassis_number
        }
        await websocket.send_text(JSONResponse(content=data).body.decode())
        await asyncio.sleep(1)

@app.websocket("/get_verified")
async def websocket_verified(websocket: WebSocket):
    await websocket.accept()
    while True:
        if verified:
            await websocket.send_text("Verified")
        else:
            await websocket.send_text("Not Verified")
        await asyncio.sleep(1)


# 📡 WebSocket endpoint to stream captured image path
@app.websocket("/get_captured_image")
async def websocket_captured_image(websocket: WebSocket):
    await websocket.accept()
    while True:
        if captured_image_path:
            # Directly use the captured image path without moving it
            image_filename = os.path.basename(captured_image_path)
            await websocket.send_text(f"/static/{image_filename}")  # Ensure the path is correctly resolved
        await asyncio.sleep(1)

# ✅ Async Capture + detect endpoint
@app.get("/capture")
async def capture_once():
    global license_plate, vehicle_details, captured_image_path
    try:
        file_path = await asyncio.to_thread(camera.capture_image)
        if file_path:
            captured_image_path = file_path  # Use the captured file path directly

            # Process license plate detection and vehicle details in parallel
            plate_task = asyncio.to_thread(detect_number_plate_vlm, captured_image_path)
            vehicle_task = asyncio.to_thread(identify_vehicle_details, captured_image_path)

            plate, vehicle_info = await asyncio.gather(plate_task, vehicle_task)

            license_plate = plate
            vehicle_details = {
                "type": vehicle_info[0],
                "brand": vehicle_info[1],
                "model": vehicle_info[2],
                "color": vehicle_info[3]
            }

            print("Updated license plate:", license_plate)
            print("Updated vehicle details:", vehicle_details)
            return {
                "status": "success",
                "plate": plate,
                "vehicle_details": vehicle_details,
                "image_path": f"/static/{os.path.basename(captured_image_path)}"
            }
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to capture image"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)



# post request to upload images
@app.post("/verification_numbers")
async def upload_verification_numbers(image: UploadFile = File(...)):
    global engine_number, chassis_number,verified
    try:
        # Save the uploaded image to a temporary file
        temp_file_path = os.path.join(CAPTURED_IMAGES_DIR, image.filename)
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(image.file, temp_file)

        # Process the image to extract engine and chassis numbers
        print("Processing image for verification numbers...")
        print(temp_file_path)
        engine_number, chassis_number = get_verification_numbers(temp_file_path)
        print("Engine Number:", engine_number)
        print("Chassis Number:", chassis_number)
        # if engine number and chasis number no empty run search
        if engine_number and chassis_number:
            vehicle_info = get_vehicle_details_by_license(engine_number)
            if vehicle_info:
                #compare 
                if vehicle_info["engine_number"] == engine_number and vehicle_info["license_no"] == chassis_number:
                    if vehicle_details["type"] == vehicle_info["type"] and vehicle_details["brand"] == vehicle_info["brand"] and vehicle_details["model"] == vehicle_info["model"] and vehicle_details["color"] == vehicle_info["color"]:
                        verified = True
                else:
                    verified = False

                return JSONResponse(content=vehicle_info)
            else:
                return JSONResponse(content={"status": "error", "message": "Vehicle not found"}, status_code=404)

        return JSONResponse(content={"engine_number": engine_number, "chassis_number": chassis_number})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    

# create a endpoint to clear all
@app.get("/clear")
async def clear_all():
    global license_plate, vehicle_details, engine_number, chassis_number, captured_image_path, verified
    license_plate = ""
    vehicle_details = {}
    engine_number = ""
    chassis_number = ""
    captured_image_path = ""
    verified = False
    return JSONResponse(content={"status": "success", "message": "All data cleared"})

