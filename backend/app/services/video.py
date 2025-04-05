import os
import cv2
import asyncio
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Video, Detection, BoundingBox
from app.services.detection import detect_people
from app.api.websockets import send_detection_update

logger = logging.getLogger(__name__)

async def process_video_file(file_path: str, video_id: int, original_filename: str):
    """Process video file to detect people using YOLO."""
    db: Session = SessionLocal()
    
    try:
        logger.info(f"Starting processing for video_id={video_id} ({original_filename})")

        # Open video
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {file_path}")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"Video loaded: {frame_count} frames at {fps:.2f} FPS")

        # Fetch video record
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"Video record not found for ID: {video_id}")
            return
        
        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_number % 5 == 0:
                timestamp = frame_number / fps
                bounding_boxes, confidences = detect_people(frame)

                if bounding_boxes:
                    detection = Detection(
                        video_id=video_id,
                        frame_number=frame_number,
                        timestamp=timestamp,
                        object_count=len(bounding_boxes)
                    )
                    db.add(detection)
                    db.flush()  # Get detection.id

                    for i, box in enumerate(bounding_boxes):
                        x1, y1, x2, y2 = box
                        conf = confidences[i]

                        db.add(BoundingBox(
                            detection_id=detection.id,
                            x1=x1, y1=y1, x2=x2, y2=y2,
                            confidence=conf
                        ))

                    db.commit()
                    logger.debug(f"Frame {frame_number}: {len(bounding_boxes)} people detected")

                    # Send WebSocket update
                    asyncio.create_task(send_detection_update(
                        video_id=video_id,
                        frame_number=frame_number,
                        object_count=len(bounding_boxes)
                    ))

            frame_number += 1

        cap.release()

        # Mark video as processed
        video.processed = 2  # 2 = Completed
        db.commit()
        logger.info(f"Finished processing video_id={video_id}")

    except Exception as e:
        logger.exception(f"Error processing video_id={video_id}: {e}")
        # Try marking video as error
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.processed = 3  # 3 = Error
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to update error status for video_id={video_id}: {db_err}")
        
    finally:
        db.close()
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed temp file: {file_path}")
