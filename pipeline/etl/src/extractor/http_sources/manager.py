import json
from pathlib import Path
from typing import Dict, List, Union
from pydantic import ValidationError
from .model import Source

from ...common.path_manager import PathManager

class SourcesManager:
    def __init__(self, path_manager:PathManager):
        self.pm = path_manager
        self.sources: Dict[str, Source] = {}

    # --- JSON FILE I/O ---
    
    def load(self):
        pass

    def save(self) -> None:
        pass

    def add_source(self, data: Dict) -> None:
        pass

    # --- Object Helper Methods ---

    def get_source(self, source_id: str) -> Source|None:
        """Retrieves a specific source configuration."""
        return self.sources.get(source_id)

    def list_sources(self) -> List[str]:
        """Returns a list of all loaded source IDs."""
        return list(self.sources.keys())

    def get_all(self) -> List[Source]:
        """Returns a list of all ETLSource objects."""
        return list(self.sources.values())