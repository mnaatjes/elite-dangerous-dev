from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
from datetime import datetime, timezone

class ManifestRecord(BaseModel):
    """
    Represents a single file entry in the manifest.
    Acts as the 'Contract' for file integrity and HTTP state.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        str_strip_whitespace=True
    )

    # --- Identity and Integrity ---
    checksum: str = Field(..., min_length=64, max_length=64)
    filename: str = Field(...)
    filepath: Path = Field(..., description="Absolute or root-relative path to the file.")
    etl_version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    is_verified: bool = False
    
    # --- HTTP Metadata ---
    etag: str | None = None
    content_type: str | None = None
    content_encoding: str | None = None
    last_modified_server: str | None = None
    content_length_bytes: int | None = Field(default=None, ge=0)
    
    # --- Local Metadata ---
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # --- Helper Methods ---

    def mark_verified(self):
        """Call this after a successful hash check."""
        self.is_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def exists(self) -> bool:
        """Check if the physical file exists on the Linux filesystem."""
        return self.filepath.exists()

    @property
    def file_size_actual(self) -> int:
        """Returns the actual size on disk in bytes."""
        if self.exists():
            return self.filepath.stat().st_size
        return 0

    def matches_server_size(self) -> bool:
        """Verifies if the downloaded file matches the Content-Length header."""
        if self.content_length_bytes is None:
            return True # Nothing to compare against
        return self.file_size_actual == self.content_length_bytes

    def to_dict(self) -> dict:
        """Convenience wrapper for model_dump."""
        return self.model_dump()

    def to_json(self, indent: int = 4) -> str:
        """Convenience wrapper for the built-in Pydantic JSON exporter."""
        return self.model_dump_json(indent=indent)