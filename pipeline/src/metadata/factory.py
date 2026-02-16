from typing import Optional, Type, TypeVar, TypedDict, Dict, Any
from typing_extensions import Unpack
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

from .models import Metadata, DownloadMetadata, SampleMetadata
from .params import DownloadParams, SampleParams

class MetadataFactory:
    """
    Central Factory for all Metadata model production
    """
    # Model Class Registry
    _model_registry = {
        "downloads": DownloadMetadata,
        "sample": SampleMetadata
    }

    @classmethod
    def _create(cls, model_key: str, **data: Any) -> Metadata:
        """
        Internal dispatcher to instantiate models from the registry.
        """
        # 1. Retrieve the class from the registry
        model_type = cls._model_registry.get(model_key)
        
        # 2. Safety check
        if not model_type:
            raise ValueError(f"Unknown Metadata model: {model_key}")
        
        # Optional: Auto-resolve paths if provided
        if "filepath" in data and isinstance(data["filepath"], Path):
            data["filepath"] = data["filepath"].resolve()

        # 3. Instantiate and return
        # Since 'data' is a dict of the kwargs, we unpack it back into the constructor
        return model_type(**data)

    @classmethod
    def create_download(cls, **properties: Unpack[DownloadParams]) -> Metadata:
        # Filter Nones to allow Pydantic's default_factory to run
        clean_props = {k: v for k, v in properties.items() if v is not None}
        return cls._create("downloads", **clean_props)
    
    @classmethod
    def create_sample(cls, **properties: Unpack[SampleParams]) -> Metadata:
        # Filter Nones to allow Pydantic's default_factory to run
        clean_props = {k: v for k, v in properties.items() if v is not None}
        return cls._create("sample", **clean_props)