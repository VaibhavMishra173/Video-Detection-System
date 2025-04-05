from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.db.database import get_db
from app.db.models import Video, Detection, BoundingBox
from app.schemas.detection import VideoSchema, DetectionResponse, VideoUploadResponse
from app.services.video import process_video_file
from app.core.config import settings
from fastapi.responses import StreamingResponse
from io import BytesIO


router = APIRouter(prefix="/api")

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check file extension
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Save file to disk
    file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    content = await file.read()
    
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Create database entry
    video = Video(filename=file.filename, filepath=file_path, data=content, processed=1)  # 1 = Processing
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Start processing in background
    background_tasks.add_task(
        process_video_file, 
        file_path=file_path, 
        video_id=video.id, 
        original_filename=file.filename
    )
    
    return {"id": video.id, "filename": file.filename, "status": "Processing started"}

@router.get("/videos", response_model=List[VideoSchema])
def get_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return [VideoSchema.from_orm(video) for video in videos]

@router.get("/videos/{video_id}", response_model=DetectionResponse)
async def get_video_detections(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    detections = (
        db.query(Detection)
        .filter(Detection.video_id == video_id)
        .all()
    )

    # Format detections with their bounding boxes
    formatted_detections = []
    for detection in detections:
        bounding_boxes = [
            {
                "x1": box.x1,
                "y1": box.y1,
                "x2": box.x2,
                "y2": box.y2,
                "confidence": box.confidence
            }
            for box in detection.bounding_boxes
        ]
        
        formatted_detections.append({
            "frame_number": detection.frame_number,
            "timestamp": detection.timestamp,
            "object_count": detection.object_count,
            "bounding_boxes": bounding_boxes
        })
    
    return {
        "id": video.id,
        "filename": video.filename,
        "upload_date": video.upload_date,
        "processed": video.processed,
        "detections": formatted_detections
    }

@router.get("/videos/{video_id}/stream")
def stream_video_from_db(video_id: int, db: Session = Depends(get_db)):
    video_info = db.query(Video).filter(Video.id == video_id).first()

    if not video_info or not video_info.data:
        raise HTTPException(status_code=404, detail="Video not found or empty")

    return StreamingResponse(BytesIO(video_info.data), media_type="video/mp4")
