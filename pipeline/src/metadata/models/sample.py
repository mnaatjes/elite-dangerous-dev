from datetime import datetime, timezone
from pydantic import Field
from typing import Optional

from .abstract import Metadata

class SampleMetadata(Metadata):
    """Metadata for a generated sample file."""
    # --- Required ---
    source_name:str
    regime_type: str
    n_rows: int
    strategy_used: str
    sampler_version: str

    # --- Optional ---
    source_offset: Optional[int]