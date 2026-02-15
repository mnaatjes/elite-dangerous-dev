from typing import TypedDict, Optional, Union
from datetime import datetime
from pathlib import Path
from ...constants import ETLProcess, ETLPipe

class SampleParams(TypedDict, total=False):
    """Input schema for create_samples factory method"""
    # From Metadata (Abstract Base)
    content_sha256: str
    filepath: Path
    etl_version: str
    pipeline: Union[ETLPipe, str]
    process: Union[ETLProcess, str]
    parent_sha256: Optional[str]
    created_at: Optional[datetime]

    # From SampleMetadata (Specific Model)
    sample_sha256: str
    regime_type: str
    n_rows: int
    source_offset: Optional[int]
    strategy_used: str
    sampler_version: str