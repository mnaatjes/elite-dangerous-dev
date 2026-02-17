from pydantic import BaseModel
from pathlib import Path
from typing import Literal

class DirConfig(BaseModel):
    data_root: Path = Path("data")
    downloads: Path = Path("data/downloads")
    manifests: Path = Path("data/manifests")
    sources: Path = Path("data/sources")
    samples: Path = Path("data/samples")
    logs: Path = Path("logs")