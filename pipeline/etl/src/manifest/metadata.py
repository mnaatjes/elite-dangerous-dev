from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

class Metadata(BaseModel):
    # auto-populate
    model_config = ConfigDict(populate_by_name=True)

    process: str
    version: str = Field(pattern=r"^\d+\.\d+$")
    total_records: int = 0
    ts_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ts_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self):
        self.ts_updated = datetime.now(timezone.utc)