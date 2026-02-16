from typing import Optional, NotRequired, Required
from .abstract import MetadataParams
from ...common.constants import CompressionType

class DownloadParams(MetadataParams):
    # --- Required ---
    source_url:str
    source_name:str
    dataset:str
    mime_type: str
    compressed_size:int
    compression_type:CompressionType|None
    is_valid:bool

    # --- Optional ---
    uncompressed_size_est:NotRequired[int]
    etag:NotRequired[str]

