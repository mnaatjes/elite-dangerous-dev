from typing import TypedDict, Optional, Any
from typing_extensions import Unpack # Use typing for 3.12+
from pathlib import Path
from datetime import datetime

from ...constants import CompressionType, ETLPipe, ETLProcess
from ..models.abstract import Metadata
from ..models.download import DownloadMetadata

class DownloadParams(TypedDict, total=False):
    """Input schema for create_downloads factory method"""
    content_sha256: str
    filepath: Path
    etl_version: str
    pipeline: ETLPipe|str
    process: ETLProcess|str
    source_url: str
    mime_type: str
    compression_type: CompressionType|str
    compressed_size: int
    is_valid: bool
    content_type: Optional[str]
    content_encoding: Optional[str]
    parent_sha256: Optional[str]
    created_at: Optional[datetime]
    downloaded_at: Optional[datetime]
    etag: Optional[str]
    uncompressed_size_est: Optional[int]
