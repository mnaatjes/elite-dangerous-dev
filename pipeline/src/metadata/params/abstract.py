from typing import TypedDict, Optional, NotRequired
from pathlib import Path
from datetime import datetime

class MetadataParams(TypedDict):
    # --- Required ---
    content_sha256:str
    file_path:Path
    version:str
    pipeline:str
    service:str
    created_at:datetime
    # --- Optional ---
    parent_sha256: NotRequired[Optional[str]]