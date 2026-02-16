from pydantic import BaseModel
from typing import Union, Literal
from datetime import datetime

class ManifestHeaders(BaseModel):
    manifest_type:Literal["download", "sample"]
    etl_version:str
    created_at:Union[str, datetime]
    updated_at:Union[str, datetime]
    record_count:int
