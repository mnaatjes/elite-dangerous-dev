from pathlib import Path
from pydantic import ValidationError

from ..path_manager import PathManager
from .models import Metadata, DownloadMetadata, SampleMetadata
from .adapters import MetadataPathAdapter

class MetadataRepository:
    
    def __init__(self, path_manager:PathManager) -> None:

        self._pm = path_manager

        # Map meta_category to _pm.generate_path() method

    def save(self, metadata:DownloadMetadata) -> Path:

        # Preform Data Validation against BaseModel schema
        try: 
            validated_data = type(metadata).model_validate(metadata.model_dump())
        except ValidationError as e:
            # TODO: Log
            raise

        # Use adapter to collect arguments from metadata obj
        # Apply arguments to naming generation / naming template
        source_args = MetadataPathAdapter.to_naming_args(validated_data)

        # Generate Target Path
        filepath = self._pm.generate_metadata_path(
            source_path=metadata.file_path,
            **source_args
        )
        # Ensure path exists before writing
        self._pm.ensure_dir_path(filepath)
        
        # Perform Write:
        self._pm.write_json(
            path=filepath,
            data=validated_data
        )

        # Return Path on success
        return filepath

