import json
from pathlib import Path
from datetime import datetime, timezone
from pydantic import ValidationError
from typing import Dict, Any
# --- Enums | Constants | Classes ---
from ..constants import ETLProcess
from .schemas.metadata_schema import ManifestMetadataSchema
# --- Class Implementation ----
class Manifest:
    # Registry container for various instances of Manifest by process attribute
    _registry = {}

    def __new__(cls, instance_name: str, *args, **kwargs):
        # --- Registry Check ---
        # Validate Instance Name against Process Enum
        if not instance_name in ETLProcess:
            raise ValueError(f"{instance_name} exists in ETLProcess ENUM")
        
        # Check that instance does NOT exist in _registry
        if instance_name not in cls._registry:
            # Create instance for instance_name
            # Store instance in registry
            instance = super().__new__(cls)
            cls._registry[instance_name] = instance

        # --- Return Instance ---
        return cls._registry[instance_name]

    def __init__(self, instance_name:str, root_dir:str|Path, etl_version:str):
        # --- Check / Initialize Instance ---
        # Check if instance created
        if not hasattr(self, "_initialized"):

            # --- Initialization Properties ---
            self.process        = instance_name
            self.root_dir       = root_dir
            self.etl_version    = etl_version

            # --- Internal State (Defaults) ---
            self.ts_executed    = datetime.now(timezone.utc)
            self.ts_created     = self.ts_executed
            self.ts_updated     = None
            self.total_records  = 0
            self.records        = {}

            # --- Define Manifest Path ---
            self.path = Path(self.root_dir / f"manifest_{self.process}_{self.etl_version}.json")

            # --- Automatic Hydration ---
            if self.path.exists():
                # Overwrite Existing Data in Manifest Object
                self.load()

            # --- Initialize Instance ---
            self._initialized = True

    @classmethod
    def list_instances(cls):
        """Returns list of instance names in cls._registry"""
        return list(cls._registry.keys())

    @classmethod
    def get_instances(cls):
        """Returns dict of instance names in cls._registry"""
        return cls._registry

    def load(self):
        """Synchronizes file state to instance"""
        pass

    def save(self):
        """Synchronizes instance state to file"""
        pass
        
    def to_json(self, indent=4) -> str:
        pass