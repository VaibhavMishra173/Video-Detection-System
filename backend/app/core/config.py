import os
import logging
from typing import List
from pydantic import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Video Detection API"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./video_detection.db"  # Replace with PostgreSQL in prod

    # File storage settings
    UPLOAD_DIR: str = "./uploads"  # Will write to disk; replace with S3 later

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

# Load and log settings
settings = Settings()
logger.info("Settings loaded:")
logger.info(f"PROJECT_NAME = {settings.PROJECT_NAME}")
logger.info(f"DATABASE_URL = {settings.DATABASE_URL}")
logger.info(f"UPLOAD_DIR = {settings.UPLOAD_DIR}")
logger.info(f"CORS_ORIGINS = {settings.CORS_ORIGINS}")
