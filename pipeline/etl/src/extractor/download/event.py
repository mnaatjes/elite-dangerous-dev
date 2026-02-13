from pydantic import BaseModel, Field, FilePath, AwareDatetime, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class DownloadEvent(BaseModel):
    # Makes Object Immutable after population
    model_config = ConfigDict(frozen=True)

    file_path: FilePath  # Validates the file actually exists on the Linux FS
    file_size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    ts_download_started: Optional[AwareDatetime] = None
    ts_download_completed: Optional[AwareDatetime] = None
    download_regime: str

    def to_dict(self) -> Dict[str, Any]:
        """Returns the model as a dictionary (useful for updating your JSON file)."""
        return self.model_dump()

    def to_json(self, indent: int = 4) -> str:
        """Returns a pretty-printed JSON string for debugging."""
        return self.model_dump_json(indent=indent)