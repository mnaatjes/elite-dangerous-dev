from pydantic import BaseModel
from typing import Union, Optional
from datetime import datetime
from .abstract_record import AbstractRecord

class DownloadRecord(AbstractRecord):
    # Required
    downloaded_at:Union[str, datetime]
    dataset:str
    source_name:str
    source_url:str
    # Optional
    etag:Optional[str] = None