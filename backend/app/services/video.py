import os
import cv2
import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Video, Detection, BoundingBox
from app.services.detection import detect_people
from app.api.websockets import send_detection_update

async def process_video_file(file_path: str, video_id: int, original_filename: str):
    """Process video file to detect people using YOLO."""
    # Open a database session
    db = SessionLocal()
    
    try:
        # Open the video file
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Update video status to processing
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return
        
        # Process frames
        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 5th frame to reduce computational load
            if frame_number % 5 == 0:
                # Calculate timestamp
                timestamp = frame_number / fps
                
                # Run detection
                bounding_boxes, confidences = detect_people(frame)
                
                # Skip if no detections
                if len(bounding_boxes) > 0:
                    # Create detection entry
                    detection = Detection(
                        video_id=video_id,
                        frame_number=frame_number,
                        timestamp=timestamp,
                        object_count=len(bounding_boxes)
                    )
                    db.add(detection)
                    db.flush()  # Get detection ID before adding bounding boxes
                    
                    # Create bounding box entries
                    for i, box in enumerate(bounding_boxes):
                        x1, y1, x2, y2 = box
                        conf = confidences[i]
                        
                        bbox = BoundingBox(
                            detection_id=detection.id,
                            x1=float(x1),
                            y1=float(y1),
                            x2=float(x2),
                            y2=float(y2),
                            confidence=float(conf)
                        )
                        db.add(bbox)
                    
                    # Commit the changes
                    db.commit()
                    
                    # Send update via WebSocket
                    asyncio.create_task(send_detection_update(
                        video_id=video_id,
                        frame_number=frame_number,
                        object_count=len(bounding_boxes)
                    ))
            
            frame_number += 1
        
        # Clean up
        cap.release()
        
        # Update video status to completed
        video.processed = 2  # 2 = Completed
        db.commit()
        
    except Exception as e:
        # Update video status to error
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.processed = 3  # 3 = Error
            db.commit()
        print(f"Error processing video: {str(e)}")
        
    finally:
        db.close()
        # Clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)