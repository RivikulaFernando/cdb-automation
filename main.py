import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from vision import detect_car_details
from camera import AxisP5522Camera

app = FastAPI()

license_plate = ""  # Stores the last detected plate


app = FastAPI()
camera = AxisP5522Camera(ip_address="169.254.40.128", username="root", password="entc")

# 🌐 Web Interface with live license plate view
@app.get("/debug")
async def get_interface():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Live License Plate</title>
        </head>
        <body>
            <h1>Detected Plate: <span id="live-data">...</span></h1>
            <script>
                const ws = new WebSocket(`wss://${location.host}/get_plate`);
                ws.onmessage = function(event) {
                    document.getElementById("live-data").textContent = event.data;
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
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(str(license_plate))
        await asyncio.sleep(1)


# ✅ NEW: Manual capture + detect endpoint
@app.get("/capture")
async def capture_once():
    global license_plate
    try:
        file_path = camera.capture_image()
        if file_path:
            plate = detect_car_details(file_path)
            license_plate = plate
            print("Updated license plate:", license_plate)
            return {"status": "success", "plate": plate, "image_path": file_path}
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to capture image"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
