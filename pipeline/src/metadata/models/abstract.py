from pydantic import BaseModel, Field, ConfigDict
from abc import ABC
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path

class Metadata(ABC,BaseModel):
    model_config = ConfigDict(frozen=True) # Metadata should be immutable

    # --- Required ---
    content_sha256: str = Field(
            ...,
            min_length=64, 
            max_length=64, 
            pattern=r"^[a-f0-9]{64}$",
            description="The SHA256 hash of this file's contents."
        )
    file_path: Path
    version: str
    pipeline: str
    service: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    # --- Optional ---
    parent_sha256:Optional[str] = None