from pydantic import Field
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
    compressed_size: int = 0
    mime_type: str
    is_valid: bool = False
    compression_type: CompressionType
    uncompressed_size_est: Optional[int] = Field(
        None,
        ge=0
    )
    content_type: Optional[str] = None
    content_encoding: Optional[str] = None
    etag: Optional[str] = None