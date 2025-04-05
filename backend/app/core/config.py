from pydantic import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Video Detection API"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./video_detection.db"
    
    # File storage settings
    UPLOAD_DIR: str = "./uploads"
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()