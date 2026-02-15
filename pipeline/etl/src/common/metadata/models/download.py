from re import S
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

from ...constants import CompressionType
from .abstract import Metadata

class DownloadMetadata(Metadata):
    """
    Metadata for raw - downloaded file
    """
    source_url: str
    downloaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    etag: Optional[str] = None
    compressed_size: int = 0
    uncompressed_size_est: Optional[int] = Field(
        None,
        ge=0
    )
    compression_type: CompressionType
    content_type: str 
    content_encoding: str
    mime_type: str
    is_valid: bool = False