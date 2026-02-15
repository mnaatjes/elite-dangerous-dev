from typing import Optional, Type, TypeVar, TypedDict, Dict, Any
from typing_extensions import Unpack
from pydantic import BaseModel

# --- Import: Metadata Models ---
from .models.abstract import Metadata
from .models.download import DownloadMetadata


#
T = TypeVar('T', bound=BaseModel)

class MetadataFactory:
    """
    Central Factory for all Metadata model production
    """
    # Model Class Registry
    _model_registry = {
        "downloads": DownloadMetadata
    }

    @classmethod
    def _create(cls, model_key, data: Dict[str, Any]) -> Metadata:
        # Capture model key
        model_type = cls._model_registry.get(model_key)
        # Validate 
        if not model_type:
            raise ValueError(f"Unknown Metadata model: {model_key}")

        # Return Validated
        return model_type(**data)

    @classmethod
    def create_downloads(cls, **properties: DownloadMetadata) -> Metadata:

        return cls._create("downloads", properties)