import re
import json
from pathlib import Path
from datetime import datetime
from typing import Type, TypeVar, Any
from pydantic import BaseModel, ValidationError, TypeAdapter

# --- Source Code ---
from etl.src.config import orchestration
from ..config.model import ETLConfig

# --- TypeVar Declarations ---
T = TypeVar("T", bound=BaseModel)

class PathManager:
    def __init__(self, config: ETLConfig):
        self.config = config
        self._root  = config.root_dir

        # Adjust root for testing environment
        if config.orchestration.testing_mode:
            self._root = self._root / "tests"

        # Ensure the root directory exists
        if not self._root.exists():
            raise NotADirectoryError(f"The Root Directory {self._root} does NOT Exist!")

    # --- Getters: Only return Path objects which SHOULD Exist; DO NOT mkdir ---

    def get_root_dir(self) -> Path:
        """Returns root directory path"""
        return self._root

    def get_downloads_dir(self) -> Path:
        return self._root / self.config.downloads.destination_dir

    def get_manifests_dir(self) -> Path:
        return self._root / self.config.downloads.manifest_dir

    def get_raw_dir(self) -> Path:
        return self._root / self.config.downloads.raw_dir


    # --- Generators: Compose and return NEW - often unique - Path obj; Never mkdir! ---

    def generate_download_path(self, source_id:str, process:str, dataset:str, version:str, extension:str) -> Path:
        """
        Generates a new timestamped path for a downloaded file
        
        NOTE: Does NOT mkdir!
        """
        # Get timestamp for <year>/<mo>/ sub directories
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # Sanitize version string
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '_')

        # Assemble Filename
        filename = f"{source_id}_{dataset}_{process}_{timestamp}_v{safe_version}{extension}"
        
        # Generate full directory path
        download_dir = self.get_downloads_dir() / now.strftime("%Y") / now.strftime("%m")

        # Return full path as Path object
        return download_dir / filename

    def generate_manifest_path(self, process:str, version:str) -> Path:
        """This method does NOT mkdir!"""
        # Sanitize version string
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '_')
        # Build and get props
        filename = f"manifest_{process.lower()}_v{safe_version}.json"
        manifest_dir = self.get_manifests_dir()
        # Return assembled path
        return manifest_dir / filename

    # --- Creators: Make the directory or path!!!; Return None ---

    def create_directory(self, path: Path) -> None:
        """Creates a Directory - if it doesn't exist"""
        path.mkdir(parents=True, exist_ok=True)

    # --- TODO: CSV I/O

    # --- JSON I/O: Simple JSON Read/Write Methods ---

    def read_json(self, path: Path) -> Any:
        """Reads and parses a JSON file into raw py object (dict or list)"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from path {path}: {e}")
    
    def write_json(self, path:Path, data:Any, atomic:bool=True) -> None:
        """
        Writes a raw py object (dict or list) to a file
        - Parent Dir MUST Exist
        - If Atomic=True: uses tmp file to prevent corruption
        """
        if atomic:
            tmp_path = path.with_suffix(f"{path.suffix}.tmp")
            with open(tmp_path, "w") as f:
                json.dump(data, f, indent=4, default=str)
            tmp_path.replace(path)
        else:
            with open(path, "w") as f:
                json.dump(data, f, indent=4, default=str)

    # --- Pydantic Model I/O: Reads/Writes JSON Files with Pydantic Models

    def read_pydantic_model(self, path:Path, model_class: Type[T]) -> T|None:
        """
        1) Reads a JSON file and validates it via Pydantic model.
        2) Returns model instance or None
        3) Raises ValueError on Validation or JSON decoding errors
        """
        # Use read_json() to get data from filepath
        raw_data = self.read_json(path)
        if raw_data is None:
            return None # file empty
        
        # Perform pydantic model validation
        try:
            # Pydantic performs validation
            # Create TypeAdapter to avoid parsing errors
            adapter = TypeAdapter(model_class)
            return adapter.validate_python(raw_data)
            #return model_class.model_validate(raw_data)
        except ValidationError as e:
            raise ValueError(f"Pydantic validation failed for {path}: {e}")
    
    def write_pydantic_model(self, path:Path, model:BaseModel, atomic:bool=True) -> None:
        """
        Writes a Pydantic model to a JSON file
        - Parent directory MUST exist
        """
        data = model.model_dump(mode="json")
        self.write_json(path, data, atomic)

