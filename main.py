import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

current_value = 0

# Simulate background updates to current_value
async def update_value():
    global current_value
    while True:
        current_value += 1
        await asyncio.sleep(2)  # simulate a new value every 2 seconds

@app.on_event("startup")
async def start_up_event():
    asyncio.create_task(update_value())

@app.get("/greet")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h1>Live Value: <span id="live-data">0</span></h1>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    document.getElementById("live-data").textContent = event.data;
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(str(current_value))
        await asyncio.sleep(1)
