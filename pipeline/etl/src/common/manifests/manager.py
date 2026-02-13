from pathlib import Path
from pydantic import ValidationError


# --- Sourcecode ---
from .model import Manifest
from ..constants import ETLProcess

class ManifestManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Check if instance created
        if cls._instance is None:
            # Generate instance
            cls._instance = super().__new__(cls)
        
        # Return Manager instance
        return cls._instance
        
    def __init__(self, root_dir:str|Path, etl_version:str):
        # Guard against re-initialization
        if hasattr(self, "_initialized"):
            return
        
        # Validate: Ensure data for setup
        if root_dir is None or etl_version is None:
            ValueError(f"Cannot initialize Manifest Manager! 'root_dir' and 'etl_version' required!")

        # Assign properties
        self.root_dir = root_dir
        self.etl_version = etl_version

        # Initialize Manager
        self._initialized = True

    def __getattr__(self, name: str):
            """
            Triggered only when mgr.<name> is called and <name> isn't an attribute.
            """
            # 1. Validate if the 'name' is a valid ETLProcess
            # This prevents creating manifests for random typos like mgr.dwonloadss
            if name not in [p.value for p in ETLProcess]:
                raise AttributeError(f"'{name}' is not a valid ETLProcess.")

            # 2. Initialize the Manifest (The Multiton logic handles the rest)
            manifest_instance = Manifest(
                instance_name=name,
                root_dir=self.root_dir,
                etl_version=self.etl_version
            )

            # 3. Optional: Cache it on the Manager so __getattr__ isn't called again 
            # for this specific process
            setattr(self, name, manifest_instance)

            return manifest_instance

    @property
    def instances(self):
        """Track and return instances from Manifest _registry"""
        return Manifest.get_instances()