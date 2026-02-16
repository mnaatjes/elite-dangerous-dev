from typing import Optional
from .abstract import MetadataParams
from ...common.constants import CompressionType

class SampleParams(MetadataParams):
    # --- Required ---
    regime_type: str
    n_rows: int
    strategy_used: str
    sampler_version: str

    # --- Optional ---
    source_offset: Optional[int]