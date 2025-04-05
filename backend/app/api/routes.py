import os
import uuid
import logging
from typing import List
from io import BytesIO

from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Video, Detection
from app.schemas.detection import VideoSchema, DetectionResponse, VideoUploadResponse
from app.services.video import process_video_file
from app.core.config import settings

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}

def is_supported_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Upload requested: {file.filename}")

    if not is_supported_file(file.filename):
        logger.warning(f"Rejected upload due to unsupported format: {file.filename}")
        raise HTTPException(status_code=400, detail="Unsupported file format")

    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    logger.info(f"Saving uploaded file to: {file_path}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info("Creating DB record for uploaded video")
    video = Video(
        filename=file.filename,
        filepath=file_path,
        data=content,  # Currently storing in DB too for /stream route
        processed=1  # 1 = Processing
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    logger.info(f"Video record created with ID: {video.id}")

    # NOTE: Later replace with S3 upload here, remove file from memory, and store key in `filepath`

    background_tasks.add_task(
        process_video_file,
        file_path=file_path,
        video_id=video.id,
        original_filename=file.filename
    )
    logger.info(f"Background processing task scheduled for video ID: {video.id}")

    return {"id": video.id, "filename": file.filename, "status": "Processing started"}


@router.get("/videos", response_model=List[VideoSchema])
def get_videos(db: Session = Depends(get_db)):
    logger.info("Fetching all uploaded videos")
    videos = db.query(Video).all()
    return [VideoSchema.from_orm(video) for video in videos]


@router.get("/videos/{video_id}", response_model=DetectionResponse)
async def get_video_detections(video_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching detections for video ID: {video_id}")
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        logger.warning(f"Video not found: ID={video_id}")
        raise HTTPException(status_code=404, detail="Video not found")

    detections = db.query(Detection).filter(Detection.video_id == video_id).all()
    logger.info(f"Found {len(detections)} detection(s) for video ID {video_id}")

    formatted_detections = [
        {
            "frame_number": det.frame_number,
            "timestamp": det.timestamp,
            "object_count": det.object_count,
            "bounding_boxes": [
                {
                    "x1": box.x1,
                    "y1": box.y1,
                    "x2": box.x2,
                    "y2": box.y2,
                    "confidence": box.confidence
                }
                for box in det.bounding_boxes
            ]
        }
        for det in detections
    ]

    return {
        "id": video.id,
        "filename": video.filename,
        "upload_date": video.upload_date,
        "processed": video.processed,
        "detections": formatted_detections
    }


@router.get("/videos/{video_id}/stream")
def stream_video_from_db(video_id: int, db: Session = Depends(get_db)):
    logger.info(f"Streaming request for video ID: {video_id}")
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video or not video.data:
        logger.warning(f"Cannot stream video ID {video_id}: Missing data")
        raise HTTPException(status_code=404, detail="Video not found or empty")

    logger.info(f"Streaming video ID {video_id}")
    return StreamingResponse(BytesIO(video.data), media_type="video/mp4")
