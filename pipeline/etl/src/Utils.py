import os
from urllib.parse import urlparse
from pathlib import Path

"""
    Utility Class for ETL Pipeline
"""

class Utils:
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Performs basic sanitization and validation on a URL.
        Ensures the URL has a valid scheme (http, https).
        """
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL format: {url}")
        if parsed_url.scheme not in ['http', 'https']:
            raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}. Only 'http' or 'https' are allowed.")
        return parsed_url.geturl()

    @staticmethod
    def validate_path(path: Path) -> Path:
        """
        Validates a given path, ensuring it's a directory and creates it if it doesn't exist.
        Returns the Path object if valid and created/exists.
        Raises ValueError if the path is not a directory or cannot be created.
        """
        if not isinstance(path, Path):
            path = Path(path)

        try:
            path.mkdir(parents=True, exist_ok=True)
            if not path.is_dir():
                raise ValueError(f"Path exists but is not a directory: {path}")
        except Exception as e:
            raise ValueError(f"Could not create or validate path '{path}': {e}")
        return path