from pydantic import BaseModel, Field, ConfigDict, DirectoryPath
from datetime import datetime, timezone
from typing import Dict, Optional
from ..constants import ETLProcess

class ManifestMetadata(BaseModel):
    """
    The 'Header' of your manifest. Handles all state and audit data.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True # Ensures types are checked even after creation
    )

    root_dir: DirectoryPath
    etl_version: str = Field(..., pattern=r"^\d+\.\d+$")
    process: ETLProcess
    
    # Use default_factory for timestamps so they are generated at instantiation
    ts_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ts_executed: Optional[datetime] = None
    ts_updated: Optional[datetime] = None
    total_records: int = Field(default=0, ge=0)

    def touch(self):
        """Helper to update the 'updated' timestamp whenever the manifest is poked."""
        self.ts_updated = datetime.now(timezone.utc)

    def sync_stats(self, records: dict):
        """Updates total_records and timestamps based on the current records dict."""
        self.total_records = len(records)
        self.touch()

    def to_json(self) -> str:
        """Dehydrate the metadata to a JSON string."""
        # by_alias=True ensures we use 'ts_created' instead of internal names if they differ
        return self.model_dump_json(indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        """Hydrate a dictionary into a ManifestMetadata object."""
        return cls.model_validate(data)