# schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List

class VideoSchema(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    processed: int

    class Config:
        orm_mode = True
