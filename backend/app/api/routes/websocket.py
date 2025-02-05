from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

ws_router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

ws_manager = WebSocketManager()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Mensaje recibido del ESP32: {data}")
    except WebSocketDisconnect:
        print("ESP32 desconectado")
        ws_manager.disconnect(websocket)

# Nuevo endpoint para enviar datos manualmente desde el backend
@ws_router.post("/send-data")
async def send_data_to_esp32(message: str):
    await ws_manager.send_message(message)
    return {"status": "Mensaje enviado", "message": message}
