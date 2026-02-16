from pathlib import Path
from typing import Any, Dict

from src.manifest.models.headers import ManifestHeaders

from ..path_manager import PathManager
from .models import Record, Manifest, Headers

class ManifestRepository:

    def __init__(self, path_manager:PathManager, manifest_type) -> None:
        self._pm = path_manager
        self.manifest_type = manifest_type

    def create(self) -> Path:
        return Path()
        pass

    def update(self) -> Path:
        return Path()
        pass

    def read(self) -> Any:
        pass

    def exists(self) -> bool:
        return False
        pass

    def get_all() -> Dict:
        return {}
        pass

    def get_by_hash(self, sha256:str) -> Dict:
        return {}
        pass

    def get_headers(self) -> Dict:
        return {}
        pass