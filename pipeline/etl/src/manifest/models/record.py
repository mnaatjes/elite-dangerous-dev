from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, AwareDatetime
from pathlib import Path
from datetime import datetime, timezone

class Record(BaseModel):
    """
    Represents a single file entry in the manifest.
    Acts as the 'Contract' for file integrity and HTTP state.
    """
    model_config = ConfigDict(frozen=True)

    source_id: str
    dataset: str
    checksum: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")
    file_path: Path
    file_size: int = Field(gt=0)
    file_version: str
    etag: Optional[str] = None
    ts_downloaded: Optional[AwareDatetime] = None