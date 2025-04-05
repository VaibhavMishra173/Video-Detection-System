from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from typing import List
from datetime import datetime
from sqlalchemy import LargeBinary


from app.db.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    data = Column(LargeBinary)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)  # 0: Not processed, 1: Processing, 2: Processed
    
    detections = relationship("Detection", back_populates="video", cascade="all, delete-orphan")

class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  # Time in seconds
    object_count = Column(Integer, nullable=False)
    
    video = relationship("Video", back_populates="detections")
    bounding_boxes = relationship("BoundingBox", back_populates="detection", cascade="all, delete-orphan")

class BoundingBox(Base):
    __tablename__ = "bounding_boxes"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"))
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    detection = relationship("Detection", back_populates="bounding_boxes")