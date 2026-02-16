from pathlib import Path
from typing import Unpack, Any
from ..path_manager import PathManager
from .models import Metadata, DownloadMetadata, SampleMetadata

class MetadataRepository:
    
    def __init__(self, path_manager:PathManager) -> None:

        self._pm = path_manager

        # Map meta_category to _pm.generate_path() method

    def save(self, metadata:Metadata):
        # Generate Target Path
        pass

