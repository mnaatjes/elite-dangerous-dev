import re
from pathlib import Path
from datetime import datetime
from etl.src.config import orchestration
from ..config.model import ETLConfig

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
    

    # --- Readers ---