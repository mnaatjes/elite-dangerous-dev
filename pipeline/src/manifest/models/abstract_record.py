from pydantic import BaseModel
from abc import ABC
from typing import Optional, Union
from pathlib import Path
from datetime import datetime

class AbstractRecord(ABC, BaseModel):
    # Required
    content_sha_256:str
    file_path:str|Path
    file_size_bytes:int
    is_compressed:bool = False
    created_at:Union[str, datetime]
    # Optional
    parent_sha256:Optional[str] = None
    file_version:Optional[str] = "1.0"

