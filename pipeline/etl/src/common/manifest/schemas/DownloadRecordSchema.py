
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DownloadRecordSchema(BaseModel):
    """Schema for single entry in 'records' dictionary"""
    filepath: str
    sha256: str = Field(min_length=64, max_length=64)
    size_bytes: int
    status: str = "competed"
    downloaded_at: datetime
    etag: Optional[str] = None
