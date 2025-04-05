from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from app.db.database import get_db
from app.db.models import Video, Detection

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, video_id: int):
        await websocket.accept()
        if video_id not in self.active_connections:
            self.active_connections[video_id] = []
        self.active_connections[video_id].append(websocket)

    def disconnect(self, websocket: WebSocket, video_id: int):
        if video_id in self.active_connections:
            self.active_connections[video_id].remove(websocket)
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]

    async def broadcast_to_video(self, video_id: int, message: Any):
        if video_id in self.active_connections:
            for connection in self.active_connections[video_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: int):
    await manager.connect(websocket, video_id)
    try:
        while True:
            # Just keep connection open, processing updates are sent from detection service
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, video_id)

# Function to be called from the video processing service
async def send_detection_update(video_id: int, frame_number: int, object_count: int):
    message = {
        "video_id": video_id,
        "frame_number": frame_number,
        "object_count": object_count
    }
    await manager.broadcast_to_video(video_id, message)