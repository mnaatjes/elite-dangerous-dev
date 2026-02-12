from pydantic import BaseModel
from typing import Optional
from .checksum_metadata import ChecksumMetadata, Field

class ProbeResult(BaseModel):
    """Container for the information gathered during probing the Source URL"""
    url: str
    status_code: int
    content_length: Optional[int] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    mime_type: str = "unknown"
    is_range_supported: bool = False
    checksum_metadata: ChecksumMetadata = Field(default_factory=ChecksumMetadata)
    probe_error: Optional[str] = None 
    