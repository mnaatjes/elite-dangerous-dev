
from pathlib import Path

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
        