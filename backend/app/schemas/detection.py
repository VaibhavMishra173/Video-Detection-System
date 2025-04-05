from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class BoundingBoxSchema(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    
    class Config:
        orm_mode = True


class DetectionSchema(BaseModel):
    frame_number: int
    timestamp: float
    object_count: int
    bounding_boxes: List[BoundingBoxSchema]
    
    class Config:
        orm_mode = True


class VideoSchema(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    processed: int  # 0: Not processed, 1: Processing, 2: Processed, 3: Error
    class Config:
        orm_mode = True


class VideoUploadResponse(BaseModel):
    id: int
    filename: str
    status: str

class DetectionResponse(VideoSchema):
    detections: List[DetectionSchema]