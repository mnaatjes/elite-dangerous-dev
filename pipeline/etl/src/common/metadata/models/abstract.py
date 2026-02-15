from pydantic import BaseModel, Field, ConfigDict
from abc import ABC
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
from ...constants import ETLProcess, ETLPipe

class Metadata(ABC,BaseModel):
    model_config = ConfigDict(frozen=True) # Metadata should be immutable

    content_sha256: str = Field(
            ...,
            min_length=64, 
            max_length=64, 
            pattern=r"^[a-f0-9]{64}$",
            description="The SHA256 hash of this file's contents."
        )

    parent_sha256: Optional[str] = Field(
        default=None,
        min_length=64, 
        max_length=64, 
        pattern=r"^[a-f0-9]{64}$",
        description="The SHA256 of the source file. Null for initial downloads."
    )

    filepath: Path = Field(
        ...,
        description="Absolute path to the artifact - i.e. the file in question."
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    etl_version: str

    pipeline: ETLPipe

    process: ETLProcess