from pathlib import Path
from typing import Unpack, Any
from ..path_manager import PathManager
from .models import Metadata, DownloadMetadata, SampleMetadata

class MetadataRepository:
    
    def __init__(self, path_manager:PathManager) -> None:

        self._pm = path_manager

        # Map meta_category to _pm.generate_path() method

    def save(self, metadata:DownloadMetadata):

        if metadata.pipeline == "download":  
            # Generate Target Path
            filename = self._pm.generate_metadata_path(
                source_path=metadata.file_path
            )

