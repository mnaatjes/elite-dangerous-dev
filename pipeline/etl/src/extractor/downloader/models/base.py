import httpx
from abc import ABC, abstractmethod
from pathlib import Path

class DownloadStrategy(ABC):
    @abstractmethod
    def download(self, url: str, destination:Path, client: httpx.Client) -> str:
        """
        Executes the download and returns the sha256 hex digest

        Requirements:
        - MUST initiate the sha256 hash prior to stream start.
        - MUST use chunked writes to destination for memory efficiency.
        - MUST utilize Constant for chunk size to ensure sha256 is consistent
        - MUST return the hex digest as a string.

        """
        pass