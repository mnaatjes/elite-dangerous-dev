
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

from .auth import Authorization as AuthModel

class Connection(BaseModel):
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
