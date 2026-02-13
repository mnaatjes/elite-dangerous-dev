import json
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any, Literal
from pathlib import Path

# --- Source Models ---
from .network import ETLNetworkSettings
from .downloads import ETLDownloadSettings
from .orchestration import ETLOrchestrationSettings

# --- Define Root Directory from which to load .env file
# >> Move up from settings.py -> config -> src -> etl root
COMPONENT_ROOT = Path(__file__).resolve().parents[2]

class ETLConfig(BaseSettings):
    # --- Find '.env' file relative to this component ---
    model_config = SettingsConfigDict(
        env_file=Path(COMPONENT_ROOT / ".env"),
        env_prefix="ETL_", # Strips prefix from .env keys
        env_nested_delimiter="__",
        extra='ignore' 
    )

    # --- Main Configuration Properties ---
    root_dir: Path = COMPONENT_ROOT
    version: str = "1.0"
    environment: Literal["dev", "staging", "production"] = "dev"
    db_connection_string: str|None = None
    user_agent: str = "ED-ETL-Pipeline"

    # --- Sub-Class Properties ---
    network: ETLNetworkSettings = ETLNetworkSettings()
    downloads: ETLDownloadSettings = ETLDownloadSettings()
    orchestration: ETLOrchestrationSettings = ETLOrchestrationSettings()

    # --- Post-Init Method ---
    def model_post_init(self, __context) -> None:
        # Ensure Directories Exist
        self._ensure_directories() 

    # --- Bootstrapper Methods ---

    def _ensure_directories(self) -> None:
        """Creates the raw, manifest, and tmp directories if they don't exist."""
        directories = [self.downloads.manifest_dir, self.downloads.destination_dir]
        if not self.root_dir.exists():
            raise NotADirectoryError(f"The ETL Root Directory {self.root_dir} does NOT EXIST!")
        for p in directories:
            # Resolve full path
            full_path = self._resolve_full_path(p)

            # Check / Create Directories
            full_path.mkdir(parents=True, exist_ok=True)

    # --- Getters and Helpers
    def _resolve_full_path(self, env_dir: str|Path) -> Path:
        # Set root directory for start of path
        dir_path = self.root_dir
        
        # Check if testing mode:
        if self.orchestration.testing_mode:
            dir_path = self.root_dir / "tests"

        return dir_path / env_dir
    
    def get_downloads_dir(self) -> Path:
        return self._resolve_full_path(self.downloads.destination_dir)
    
    def get_manifests_dir(self) -> Path:
        return self._resolve_full_path(self.downloads.manifest_dir)
    
    def get_raw_dir(self) -> Path:
        return self._resolve_full_path(self.downloads.raw_dir)

    # --- Debugging Methods ---

    def to_dict(self, mask_sensitive: bool = True) -> Dict[str, Any]:
        """Returns a dictionary of the current settings."""
        data = self.model_dump()
        
        if mask_sensitive:
            # Mask the password in the connection string if present
            if "db_connection_string" in data and data["db_connection_string"]:
                # Simple mask: keep scheme, hide the rest
                # e.g., postgresql://user:pass@host -> postgresql://****
                scheme = data["db_connection_string"].split("://")[0]
                data["db_connection_string"] = f"{scheme}://****"
                
        return data

    def to_json(self, indent: int = 4, mask_sensitive: bool = True) -> str:
        """Returns a pretty-printed JSON string of the settings."""
        return json.dumps(self.to_dict(mask_sensitive=mask_sensitive), indent=indent, default=str)