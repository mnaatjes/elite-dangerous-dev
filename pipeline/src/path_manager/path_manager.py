import errno
import json
from pathlib import Path
from typing import Any, Unpack
from datetime import datetime

# --- Dependencies ---
from src.config import Config
from .naming import NamingService

# --- Arguments ---
from .args import DownloadsArgs, LogArgs, ManifestArgs, MetadataArgs, SampleArgs

class PathManager:
    def __init__(self, settings:Config, naming:NamingService) -> None:
        # Apply dependencies
        self.settings   = settings
        self._root      = self.settings._root
        self.naming     = naming

        # Ensure Root Directory Exists
        if not self._root.exists():
            raise NotADirectoryError(f"The Root Directory {self._root} does NOT Exist!")
        
        # Ensure major directories are present
        self._verify_infrastructure()

    def _verify_infrastructure(self):
        """
        Ensures major directories exist
        """
        for dir_name, path in self.settings.dir.model_dump().items():
            if not path.exists():
                raise FileNotFoundError(
                    errno.ENONET, # No such file error number
                    f"ETL Directory '{dir_name}' Missing",
                    str(path)
                )
        
    # --- Getters: Only return Path objects which SHOULD Exist; DO NOT mkdir ---

    def get_root_dir(self) -> Path:
        """Returns root directory path"""
        return self._root
    
    def get_data_dir(self) -> Path:
        return self.settings.dir.base_data

    def get_downloads_dir(self) -> Path:
        return self.settings.dir.downloads
    
    def get_sources_dir(self) -> Path:
        return self.settings.dir.sources

    def get_samples_dir(self) -> Path:
        return self.settings.dir.samples

    def get_manifests_dir(self) -> Path:
        return self.settings.dir.manifests
    
    def get_logs_dir(self) -> Path:
        return self.settings.dir.logs

    # --- Generators: Return Path() object: DO NOT MKDIR! ---
    
    def generate_download_path(self, **kwargs: Unpack[DownloadsArgs]) -> Path:
        # Get filename from naming service
        filename = self.naming.generate("downloads", **kwargs)

        # Generate the nested filepaths in downloads/<year>/<mo>
        # Get timestamp for <year>/<mo>/ sub directories
        now = datetime.now()
        dir_path = self.get_downloads_dir() / now.strftime("%Y") / now.strftime("%m")

        # Return Completed Filepath
        return Path( dir_path / filename)
    
    def generate_manifest_path(self, **kwargs: Unpack[ManifestArgs]) -> Path:
        # Get filename from naming service
        filename = self.naming.generate("manifest", **kwargs)
        return Path( self.get_manifests_dir() / filename)
    
    def generate_metadata_path(self, source_path:Path, **kwargs: Unpack[MetadataArgs]) -> Path:
        # Get filename from naming service
        filename = self.naming.generate("metadata", **kwargs)
        return Path( source_path / filename)
    
    def generate_log_path(self, **kwargs: Unpack[LogArgs]) -> Path:
        # Get filename from naming service
        filename = self.naming.generate("log", **kwargs)
        return Path( self.get_logs_dir() / filename)
    
    def generate_sample_path(self, **kwargs: Unpack[SampleArgs]) -> Path:
        # Form Filename from naming service
        filename = self.naming.generate("sample", **kwargs)

        # Generate the nested filepaths in downloads/<year>/<mo>
        # Get timestamp for <year>/<mo>/ sub directories
        now = datetime.now()
        dir_path = self.get_samples_dir() / now.strftime("%Y") / now.strftime("%m")

        # Return Completed Filepath
        return Path( dir_path / filename)

    # --- Creators: Make the directory or path!!!; Return None ---

    def create_directory(self, path: Path) -> None:
        """Creates a Directory - if it doesn't exist"""
        path.mkdir(parents=True, exist_ok=True)

    # --- JSON I/O: Simple JSON Read/Write Methods ---

    def read_json(self, path: Path, strict:bool = True) -> Any:
        """Reads and parses a JSON file into raw py object (dict or list)"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Check for strict
            if strict:
                return None
            # Non-strict Mode
            raise FileNotFoundError(f"Manifest File not found at path {path}")
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