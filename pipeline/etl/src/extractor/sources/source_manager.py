import json
from pathlib import Path
from typing import Dict, List, Union
from pydantic import ValidationError
from .model import ETLSource

class SourcesManager:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.sources: Dict[str, ETLSource] = {}
        self.load_from_file()

    def load_from_file(self) -> None:
        """Reads the JSON file and hydrates the ETLSource objects."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Source file not found at: {self.file_path}")

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
                # Handle both a single object or a list of objects
                if isinstance(data, dict):
                    # If your JSON is a map of {id: data}
                    for sid, sdata in data.items():
                        self._add_source(sdata)
                elif isinstance(data, list):
                    # If your JSON is a flat list of objects
                    for sdata in data:
                        self._add_source(sdata)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except ValidationError as e:
            print(f"Data validation failed: {e}")

    def _add_source(self, data: Dict) -> None:
        """Internal helper to hydrate and store a source."""
        source = ETLSource.load(data)
        self.sources[source.source_id] = source

    def get_source(self, source_id: str) -> ETLSource|None:
        """Retrieves a specific source configuration."""
        return self.sources.get(source_id)

    def save_sources(self) -> None:
        """Persists the current state of all sources back to the JSON file."""
        output = [source.to_dict() for source in self.sources.values()]
        with open(self.file_path, 'w') as f:
            json.dump(output, f, indent=4)
        print(f"Successfully saved {len(output)} sources to {self.file_path}")

    def list_sources(self) -> List[str]:
        """Returns a list of all loaded source IDs."""
        return list(self.sources.keys())

    def get_all(self) -> List[ETLSource]:
        """Returns a list of all ETLSource objects."""
        return list(self.sources.values())