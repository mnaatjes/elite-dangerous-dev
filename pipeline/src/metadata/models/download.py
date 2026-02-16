from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

from ...common.constants import CompressionType
from .abstract import Metadata

class DownloadMetadata(Metadata):
    """
    Metadata for raw - downloaded file
    """
    source_url: str
    source_name:str
    dataset:str
    mime_type: str
    compressed_size: int = 0
    compression_type: CompressionType|None
    is_valid: bool = False

    # --- Optional Properties ---
    uncompressed_size_est: Optional[int] = Field(
        None,
        ge=0
    )
    etag: Optional[str] = None
