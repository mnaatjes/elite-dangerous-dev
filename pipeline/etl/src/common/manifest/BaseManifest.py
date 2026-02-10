import os
import json
from abc import ABC
from typing import Dict, Any, Type
from pathlib import Path

class BaseManifest(ABC):
    def __init__(self, path: Path|str):
        self.path = Path(path) if isinstance(path, str) else path
        self.data: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            with open(self.path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Manifest filepath {self.path} does NOT exist!")

    def save(self):
        # Ensure directory exists on Linux
        # TODO: Change how this is done!
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def update(self, key: str, value: Dict[str, Any]):
        # Here you would call your schema validation
        self.data[key] = value
        self.save()