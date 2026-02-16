from pydantic import BaseModel
from typing import Dict, Any

class Manifest(BaseModel):
    headers:dict
    records: Dict[str, Any]
