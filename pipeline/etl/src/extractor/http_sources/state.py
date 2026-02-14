from pydantic import BaseModel
from typing import Optional

class State(BaseModel):
    last_etag: Optional[str] = None
    last_sha256: Optional[str] = None
    last_run: Optional[str] = None