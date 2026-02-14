
from typing import Dict, Type, Any
from pydantic import BaseModel, Field, model_validator

from .metadata import Metadata as ManifestMeta
from .record import Record as ManifestRecord

class Manifest(BaseModel):
    """ The primary Manifest object."""
    process: str
    metadata: ManifestMeta
    # Dictionary mapping SHA256 strings to Record objects
    records: Dict[str, ManifestRecord] = Field(default_factory=dict)

    # --- Pydantic Methods ---

    @model_validator(mode="after")
    def validate_record_keys(self) -> "Manifest":
        """Ensures the dict keys actually match the record checksums."""
        for sha, record in self.records.items():
            if sha != record.checksum:
                raise ValueError(
                    f"Manifest key mismatch: Key '{sha}' does not match "
                    f"Record checksum '{record.checksum}'"
                )
        return self