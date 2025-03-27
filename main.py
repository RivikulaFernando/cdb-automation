import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from vision import detect_car_details
from camera import capture_image
from contextlib import asynccontextmanager

app = FastAPI()

license_plate = ""  # Stores the last detected plate


# 🔄 Background task to update license plate continuously
async def update_plate():
    global license_plate
    while True:
        try:
            file_path = capture_image("169.254.160.88", "root", "entc", "captures")
            if file_path:
                plate = detect_car_details(file_path)
                license_plate = plate
                print("Updated license plate:", plate)
        except Exception as e:
            print("Auto-detect error:", e)
        await asyncio.sleep(5)


# 🚀 Run background updater on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(update_plate())
    yield  # runs the app
    # You can do cleanup after the app stops here

app = FastAPI(lifespan=lifespan)


# 🌐 Web Interface with live license plate view
@app.get("/greet")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Live License Plate</title>
        </head>
        <body>
            <h1>Detected Plate: <span id="live-data">...</span></h1>
            <script>
                const ws = new WebSocket(`ws://${location.host}/ws`);
                ws.onmessage = function(event) {
                    document.getElementById("live-data").textContent = event.data;
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# 📡 WebSocket endpoint to stream live license plate
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(license_plate)
        await asyncio.sleep(1)


# ✅ NEW: Manual capture + detect endpoint
@app.get("/capture")
async def capture_once():
    global license_plate
    try:
        file_path = capture_image("169.254.160.88", "root", "entc", "captures")
        if file_path:
            plate = detect_car_details(file_path)
            license_plate = plate
            return {"status": "success", "plate": plate, "image_path": file_path}
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to capture image"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
