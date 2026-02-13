from pydantic import BaseModel, ConfigDict
from pathlib import Path

class ETLDownloadSettings(BaseModel):
    """Specific settings for the extraction/download phase."""
    # Paths relative to etl_root
    # Note: We use relative paths here so ETLConfig can derive 
    # the absolute paths via @computed_field
    raw_dir: Path = Path("data/raw")
    destination_dir: Path = Path("data/downloads")
    manifest_dir: Path = Path("data/manifests")
    
    # Network settings specific to downloads
    user_agent: str = "Elite-Dangerous-ETL/1.0"
    timeout: int = 30
    chunk_size: int = 128 * 1024  # 128KB

    # Prevents 'extra_forbidden' errors if .env has unexpected keys
    model_config = ConfigDict(extra='ignore')