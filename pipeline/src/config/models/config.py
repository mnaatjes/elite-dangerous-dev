
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal

# --- Load other Models ---
from .directories import DirConfig
from .network import NetworkConfig

# --- Define Root Directory from which to load .env file
# >> Move up from settings.py -> config -> src -> etl root
COMPONENT_ROOT = Path(__file__).resolve().parents[3]

class Config(BaseSettings):
    # --- Find '.env' file relative to this component ---
    model_config = SettingsConfigDict(
        env_file=Path(COMPONENT_ROOT / ".env.test"),
        env_prefix="ETL_", # Strips prefix from .env keys
        env_nested_delimiter="__",
        extra='ignore' 
    )

    # --- Main Configuration Properties ---
    _root: Path = COMPONENT_ROOT
    version: str = "1.0"
    environment: Literal["dev", "staging", "production"] = "dev"

    # --- Directory Map ---
    dir: DirConfig = DirConfig()

    # --- Network Configurations ---
    network: NetworkConfig = NetworkConfig()