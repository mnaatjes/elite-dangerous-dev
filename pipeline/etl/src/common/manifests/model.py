import json
from pathlib import Path
from datetime import datetime, timezone
from pydantic import ValidationError
from typing import Dict, Any
# --- Enums | Constants | Classes ---
from ..constants import ETLProcess
from .metadata import ManifestMetadata
from .record import ManifestRecord

# --- Class Implementation ----
class Manifest:
    # Registry container for various instances of Manifest by process attribute
    _registry = {}

    def __new__(cls, instance_name: str, *args, **kwargs):
        # --- Registry Check ---
        # Validate Instance Name against Process Enum
        if not instance_name in ETLProcess:
            raise ValueError(f"{instance_name} does not exist in ETLProcess ENUM")
        
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
        if hasattr(self, "_initialized"):
            return

        # --- 1. Validate inputs via ManifestMetadata ---
        # This performs Pydantic validation immediately
        self.metadata = ManifestMetadata(
            process=instance_name,
            root_dir=root_dir,
            etl_version=etl_version
        )

        # --- 2. Setup Records Container ---
        # Keyed by SHA256 as requested
        self.records: Dict[str, ManifestRecord] = {}

        # --- 3. Define the File Path ---
        # Using .value because process is an Enum
        filename = f"{self.metadata.process.value}_v{self.metadata.etl_version}.json"
        self.path = Path(self.metadata.root_dir) / filename

        # --- 4. Automatic Hydration ---
        # Replaces values from file if file exists
        if self.path.exists():
            self.load()
        else:
            # First time setup
            self.metadata.ts_created = self.metadata.ts_created # already set by default_factory

        self._initialized = True

    @classmethod
    def list_instances(cls):
        """Returns list of instance names in cls._registry"""
        return list(cls._registry.keys())

    @classmethod
    def get_instances(cls):
        """Returns dict of instance names in cls._registry"""
        return cls._registry

    def add_record(self, record_params: dict):
        """
        Orchestrates adding a record:
        Validates data -> Updates memory -> Syncs Metadata -> Saves to Linux
        """
        # Create the Pydantic object (validates input)
        record = ManifestRecord(**record_params)
        
        # Store using checksum as the key
        self.records[record.checksum] = record
        
        # Sync metadata stats
        self.metadata.total_records = len(self.records)
        self.metadata.touch()
        
        # Persist to disk
        self.save()

    def save(self):
        """Atomic save to prevent manifest corruption."""
        # Dehydrate everything for JSON
        output = {
            "metadata": self.metadata.model_dump(mode="json"),
            "records": {sha: rec.model_dump(mode=json) for sha, rec in self.records.items()}
        }
        
        temp_path = self.path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            import json
            json.dump(output, f, indent=4)
        
        temp_path.replace(self.path)

    def load(self):
        """Hydrates the class from the Linux filesystem."""
        with open(self.path, "r") as f:
            import json
            data = json.load(f)
            
            # Hydrate Metadata
            self.metadata = ManifestMetadata.model_validate(data["metadata"])
            
            # Hydrate Records
            self.records = {
                sha: ManifestRecord.model_validate(rec) 
                for sha, rec in data.get("records", {}).items()
            }

    def inspect(self) -> dict:
        """
        Returns the entire manifest state as a dictionary.
        Perfect for debugging with pprint or logging.
        """
        return {
            "metadata": self.metadata.model_dump(),
            "records": {
                sha: record.model_dump() 
                for sha, record in self.records.items()
            }
        }