from ...common.path_manager import PathManager
from .factory import MetadataFactory
from .models.abstract import Metadata
from pathlib import Path

class MetadataRepository:

    def __init__(self, path_manager:PathManager, meta_factory:MetadataFactory) -> None:
        # Dependencies
        self.pm = path_manager
        self.factory = meta_factory


    def save(self, metadata: Metadata) -> Path:
        meta_filepath = self.pm.generate_metadata_path(metadata.filepath)
        
        self.pm.write_pydantic_model(
            path=self.pm.generate_metadata_path(metadata.filepath),
            model=metadata,
            atomic=False
        )

        return Path(meta_filepath)
    
    def load(self, filepath: Path) -> Metadata:
        # Use path manager to read json
        data = self.pm.read_json(
            path=filepath
        )

        # Check for None
        if not data:
            raise ValueError(f"No metadata loaded from path: {filepath}")
        
        # Extract model_key from json data
        model_key = data.get("process")

        # Determine process and hydrate
        # TODO: Find way to decouple
        if model_key == "downloads":
            return self.factory.create_download(**data)
        elif model_key == "sample":
            return self.factory.create_sample(**data)
        
        raise ValueError(f"Unknown or missing model_key '{model_key}' in {filepath}")
        # Hydrate
        

