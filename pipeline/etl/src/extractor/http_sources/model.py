from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import re
from pathlib import Path
from urllib.parse import urlparse

from .connection import Connection as ConnectionModel
from .state import State as StateModel

class Source(BaseModel):
    source_id: str
    source_type: str = "file"
    dataset: str
    expected_format: str = "json"
    compression: str = "gzip"
    connection: ConnectionModel = Field(default=ConnectionModel())
    state: StateModel = Field(default_factory=StateModel)

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