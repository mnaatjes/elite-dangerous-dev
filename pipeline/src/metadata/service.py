from pathlib import Path
from typing import Unpack, Any
from .models import Metadata, DownloadMetadata, SampleMetadata
from .repository import MetadataRepository
from .params import DownloadParams

class MetadataService:

    def __init__(self, settings, path_manager) -> None:
        self._settings = settings
        self._repo = MetadataRepository(path_manager)

    def register_download(self, **kwargs:Unpack[DownloadParams]) -> None:
        """High-level method provided by service for generating download metadata file"""
        # Assign as single object
        metadata = DownloadMetadata(**kwargs)
        self._repo.save(metadata)