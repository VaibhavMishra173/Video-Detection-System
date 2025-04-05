import json
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Video, Detection

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, video_id: int):
        await websocket.accept()
        if video_id not in self.active_connections:
            self.active_connections[video_id] = []
        self.active_connections[video_id].append(websocket)
        logger.info(f"WebSocket connected for video_id={video_id}. Total connections: {len(self.active_connections[video_id])}")

    def disconnect(self, websocket: WebSocket, video_id: int):
        if video_id in self.active_connections:
            self.active_connections[video_id].remove(websocket)
            logger.info(f"WebSocket disconnected for video_id={video_id}. Remaining: {len(self.active_connections[video_id])}")
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]
                logger.info(f"No more connections for video_id={video_id}. Entry removed.")

    async def broadcast_to_video(self, video_id: int, message: Any):
        if video_id in self.active_connections:
            for connection in self.active_connections[video_id]:
                try:
                    await connection.send_json(message)
                    logger.debug(f"Sent message to video_id={video_id}: {message}")
                except Exception as e:
                    logger.error(f"Failed to send message to video_id={video_id}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: int):
    await manager.connect(websocket, video_id)
    try:
        while True:
            await websocket.receive_text()  # Keeps connection alive; no-op for now
    except WebSocketDisconnect:
        manager.disconnect(websocket, video_id)
        logger.info(f"WebSocket disconnected (clean) for video_id={video_id}")
    except Exception as e:
        logger.error(f"WebSocket error for video_id={video_id}: {e}")
        manager.disconnect(websocket, video_id)

# Function to be called from the video processing service
async def send_detection_update(video_id: int, frame_number: int, object_count: int):
    message = {
        "video_id": video_id,
        "frame_number": frame_number,
        "object_count": object_count
    }
    logger.info(f"Broadcasting detection update: {message}")
    await manager.broadcast_to_video(video_id, message)
