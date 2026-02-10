import json
from abc import ABC
from typing import Dict, Any, Type, TypeVar, Generic
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime, timezone
from .ManifestEncoder import ManifestEncoder
from .schemas.ManifestSchema import ManifestSchema

# Create a Type Variable for Pydantic BaseModel
T = TypeVar("T", bound=BaseModel)

class BaseManifest(ABC, Generic[T]):
    #def __init__(self, root_dir: Path|str, process:str, domain:str, etl_version:str, schema: Type[T]):
    def __init__(self, schema: ManifestSchema):
        # Format root_dir
        if isinstance(schema.root_dir, str):
            root_dir = Path(schema.root_dir)

        # Validate root_dir
        if not root_dir.is_dir():
            raise NotADirectoryError(f"The manifest root directory: {root_dir} does NOT exist!")
        
        # Compose Filename for Manifest
        filename = f"{schema.domain}_{schema.process}.manifest.json"

        # --- Assign Properties ---
        self.path    = Path(root_dir / filename)
        self.process = schema.process
        self.domain  = schema.domain
        self.version = schema.etl_version
        # If a schema parameter - store for update()
        self.record_schema  = schema.record_schema

        # Load Data from File / New Schema
        self.data: Dict[str, Any] = self.load()

    def __repr__(self) -> str:
            """
            Returns a developer-friendly representation of the Manifest instance.
            Matches the properties validated by ManifestSchema.
            """
            return (
                f"{self.__class__.__name__}("
                f"domain='{self.domain}', "
                f"process='{self.process}', "
                f"version='{self.version}', "
                f"path='{self.path}', "
                f"schema={self.record_schema.__name__ if self.record_schema else None}, "
                f"record_count={len(self.data.get('records', {}))}"
                f")"
            )

    def load(self) -> Dict[str, Any]:
        if self.path.exists() and self.path.is_file():
            with open(self.path, 'r') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "manifest_type": self.__class__.__name__.lower(),
                    "process": self.process,
                    "domain": self.domain,
                    "version": self.version,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": None,
                },
                "records": {}
            }
        
    def save(self):
        # root_dir validated in constructor
        # Uses ManifestEncoder to make JSON safe properties
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4, cls=ManifestEncoder)

    def update(self, key:str, record_data: Dict[str, Any]):
        """
            Adds of updates a record and commits it to disk using self.save() method

        """
        # Ensure dict is passed
        if not isinstance(record_data, dict):
            raise TypeError(f"Parameter 'record_data' must be a dict! Got type: {type(record_data).__name__}")
        
        # Determine if record schema exists
        if self.record_schema:
            # Will raise error if record_data missing a field
            validated_data = self.record_schema(**record_data).model_dump()
            self.data["records"][key] = validated_data
        else:
            # Update specific record without schema
            self.data["records"][key] = record_data

        # Update global metadata timestamp
        self.data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Commit to filesystem
        self.save()