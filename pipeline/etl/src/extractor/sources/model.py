from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import json
import re
from pathlib import Path
from urllib.parse import urlparse

class AuthModel(BaseModel):
    type: str = ""
    config: str = ""

class ConnectionModel(BaseModel):
    url: str = ""  # Using str to allow empty defaults, change to HttpUrl for strictness
    method: str = "GET"
    timeout: int = 7200
    frequency_cron: Optional[str] = None
    retry_policy: Optional[Dict[str, Any]] = None
    auth: AuthModel = Field(default_factory=AuthModel)
    headers: Dict[str, str] = Field(default_factory=dict)
    source_type: str = ""

    @field_validator("url")
    @classmethod
    def validate_url_protocol(cls, v: str) -> str:
        # Skip validation for empty default strings
        if not v:
            return v
            
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"URL must use http or https protocol. Received: {parsed.scheme}")
        if not parsed.netloc:
            raise ValueError(f"URL is missing a valid domain/netloc: {v}")
        return v

    @property
    def domain(self) -> str:
        """Helper to extract the domain (e.g., spansh.co.uk) for logs or pathing."""
        if not self.url:
            return "unknown"
        return urlparse(self.url).netloc

class StateModel(BaseModel):
    last_etag: Optional[str] = None
    last_sha256: Optional[str] = None
    last_run: Optional[str] = None

class ETLSource(BaseModel):
    source_id: str
    source_type: str = "file"
    dataset: str
    expected_format: str = "json"
    compression: str = "gzip"
    connection: ConnectionModel = Field(default=ConnectionModel())
    state: StateModel = Field(default_factory=StateModel)

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "ETLSource":
        """Hydrates the model from a dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the model as a dictionary (useful for updating your JSON file)."""
        return self.model_dump()

    def to_json(self, indent: int = 4) -> str:
        """Returns a pretty-printed JSON string for debugging."""
        return self.model_dump_json(indent=indent)

    @property
    def full_extension(self) -> str:
        """
        Extracts multi-part extensions from the URL (e.g., '.json.gz').
        Returns an empty string if no extension is found.
        """
        if not self.connection.url:
            return ""

        # Extract the filename from the end of the URL path
        path_name = urlparse(self.connection.url).path
        filename = Path(path_name).name

        # Regex explanation:
        # Find the first dot that is followed by alphanumeric characters, 
        # capturing everything from that dot to the end of the string.
        match = re.search(r'(\.[a-z0-9.]+)$', filename, re.IGNORECASE)
        
        return match.group(1) if match else ""