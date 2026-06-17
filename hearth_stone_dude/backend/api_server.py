import asyncio
import json
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.log_monitor import LogMonitor
from backend.card_tracker import CardTracker
from backend.config import Config


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        for connection in disconnected:
            self.active_connections.discard(connection)


app = FastAPI(title="HearthStone Dude API")
manager = ConnectionManager()
card_tracker = CardTracker()
log_monitor = LogMonitor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def on_packet_tree(packet_tree):
    card_tracker.update(packet_tree)
    tracking_data = card_tracker.get_tracking_data()
    
    asyncio.create_task(manager.broadcast(tracking_data))


log_monitor.set_on_packet_tree_callback(on_packet_tree)


@app.get("/")
async def root():
    return {"message": "HearthStone Dude API Server"}


@app.get("/api/status")
async def get_status():
    return card_tracker.get_tracking_data()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json(card_tracker.get_tracking_data())
        
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    Config.ensure_dirs()
    log_monitor.start()


@app.on_event("shutdown")
async def shutdown_event():
    log_monitor.stop()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
