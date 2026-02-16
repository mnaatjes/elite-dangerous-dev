from pydantic import BaseModel
from pathlib import Path
from typing import Literal


class NetworkConfig(BaseModel):
    user_agent:str = "ED-ETL-Pipeline"
    timeout:int = 5
    chunk_size_bytes:int = 1024 # 1KB
    max_file_size_bytes:int = 52428800 # 50MB
    max_retries:int = 1