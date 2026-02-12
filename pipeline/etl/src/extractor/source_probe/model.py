from pydantic import BaseModel
from typing import Optional

class ProbeResult(BaseModel):
    """Container for the information gathered during probing the Source URL"""
    url: str
    status_code: int
    content_length: Optional[int] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    mime_type: Optional[str] = None
    is_range_supported: bool = False
    # Additional properties to include?
    # - Content-Type
    # - Content-Encoding
    # - MD-5
    # - sha256
    # - Other checksums, content information, etc
    