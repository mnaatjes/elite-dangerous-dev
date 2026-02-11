
from pydantic import BaseModel, Field, DirectoryPath, ConfigDict
from typing import Union
from pathlib import Path

class FileRecordSchema(BaseModel):
    # Allows the schema to handle complex types like 'Type' or 'Path'
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # --- Idenitity and Integrity Fields ---
    checksum: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="sha256 generated from content by downloader. For verification and ID"
    )
    filename: str = Field(
        ...,
        description="Final Filename of reference download file"
    )
    # Using Union for Python < 3.10 compatibility; otherwise str | Path is fine
    filepath: Union[str, Path] = Field(
        ..., 
        description="Path relative to the root_dir."
    )
    etl_version: str = Field(
        default="1.0.0", 
        pattern=r"^\d+\.\d+$", # Enforces Semantic Versioning (e.g., 1.2.3)
        description="The version of the ETL logic creating this manifest."
    )
    is_verified: bool = Field(
        default=False,
        description="Set to True after the post-download chunked re-hash succeeds."
    )

    # --- HTTP Metadata ---
    
    etag: str | None = Field(default=None, description="Server-provided ETag for conditional GETs.")
    content_type: str|None = None
    content_encoding: str|None = None
    last_modified_server: str|None = None
    content_length_bytes: int | None = Field(
        default=None, 
        ge=0, 
        description="Size as reported by the server headers."
    )
