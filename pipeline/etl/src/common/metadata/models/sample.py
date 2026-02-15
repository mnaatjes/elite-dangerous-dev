from datetime import datetime, timezone
from pydantic import Field
from typing import Optional

from .abstract import Metadata

class SampleMetadata(Metadata):
    """Metadata for a generated sample file."""
    sample_sha256: str = Field(..., description="SHA256 hash of the sample file content.")
    regime_type: str = Field(..., description="Type of sampling performed (e.g., 'head', 'random', 'systematic').")
    n_rows: int = Field(..., description="Number of records captured in the sample.")
    source_offset: Optional[int] = Field(None, description="Starting position in the source file.")
    strategy_used: str = Field(..., description="Name of the sampling strategy class used.")
    sampler_version: str = Field("1.0", description="Version of the sampler logic.")