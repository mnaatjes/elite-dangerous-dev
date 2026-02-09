import os
import re
import requests
import mimetypes
import magic
import warnings

from typing import Literal, Optional
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

"""
    Utility Class for ETL Pipeline
"""

class Utils:
    # Constants
    NON_SPECIFIC_CONTENT_TYPES = [
        "",
        None,
        "text/plain",
        "application/unknown",
        "application/octet-stream",
        "binary/octet-stream"
    ]
    STANDARD_CONTENT_ENCODINGS = ['gzip', 'deflate', 'br', 'identity']

    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Performs basic sanitization and validation on a URL.
        Ensures the URL has a valid scheme (http, https).
        Adds hostname validation for common invalid patterns.
        """
        url_stripped = url.strip() # Remove leading/trailing whitespace

        parsed_url = urlparse(url_stripped)

        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL format: Missing scheme or network location in '{url_stripped}'")
        if parsed_url.scheme not in ['http', 'https']:
            raise ValueError(f"Unsupported URL scheme: '{parsed_url.scheme}'. Only 'http' or 'https' are allowed for '{url_stripped}'.")

        hostname = parsed_url.hostname

        # Basic hostname validation
        if not hostname:
            raise ValueError(f"Invalid URL format: Hostname is empty in '{url_stripped}'")
        if hostname.startswith('-') or hostname.endswith('-'):
            raise ValueError(f"Invalid hostname: Hostname cannot start or end with a hyphen in '{url_stripped}'.")
        if '_' in hostname:
            raise ValueError(f"Invalid hostname: Hostname cannot contain an underscore in '{url_stripped}'.")

        return parsed_url.geturl()

    @staticmethod
    def validate_path(path: Path, expected_type: Literal['file', 'dir']) -> Path:
        """
        Validates a given path, ensuring it's a directory and creates it if it doesn't exist.
        Returns the Path object if valid and created/exists.
        Raises ValueError if the path is not a directory or cannot be created.
        """
        if not isinstance(path, Path):
            path = Path(path)

        # Check file / dir exists
        if not path.exists():
            raise ValueError(f"Provided path {path} does not exist!")

        # Check if directory
        if expected_type == 'dir' and not path.is_dir():
            raise ValueError(f"Provided path {path} is NOT a directory! Expected type defined as {expected_type}")

        # Check if filepath
        if expected_type == "file" and not path.is_file():
            raise ValueError(f"Provided path {path} is NOT a file as expected: {expected_type}")


        # Passed validation
        # Return Path object
        return path

    @staticmethod
    def hello(msg: str) -> None:
        print(f"Hello, {msg}")

    @staticmethod
    def get_content_headers(url: str) -> dict:

        # Request headers
        res = requests.head(url, allow_redirects=True, timeout=5)
        # Raise exceptions
        res.raise_for_status()
        # Return content type and content encoding
        return {
            "Content-Type": res.headers.get('Content-Type', '').lower(),
            "Content-Encoding": res.headers.get('Content-Encoding', '').lower()
        }

    @staticmethod
    def get_url_extensions(url: str) -> list:
        # Declare extensions acc
        extensions = []

        # Parse and get URL Path
        parsed_url = urlparse(url)
        filepath = parsed_url.path

        # Get ext and root path
        # Loop until all extensions collected
        root, ext = os.path.splitext(filepath)
        while ext:
            # Add to top of stack to maintain order
            extensions.insert(0, ext)
            # Perform another extraction
            root, ext = os.path.splitext(root)
            # Check if filename was just .ext
            if not root and ext:
                break
            elif root.startswith("."):
                extensions.insert(0, root)
                break
        
        # Return Extensions
        return extensions

    @staticmethod
    def guess_url_mime_type(url: str) -> str:

        # Parse url
        parsed_url = urlparse(url)
        filepath = parsed_url.path

        # Guess Type
        type, encoding = mimetypes.guess_type(filepath)
        
        # Return dict
        return {
            "Content-Type": type,
            "Content-Encoding": encoding
        }
    
    @staticmethod
    def get_type_from_sample(url: str) -> str:

        # Perform http request
        res = requests.get(url, stream=True, timeout=10)
        # Raise exceptions
        res.raise_for_status()

        # Extract sample
        # Close connection
        sample = res.raw.read(1024)
        res.close()

        # Read sample
        # Detect mime type
        # Returns Content-Type
        return magic.from_buffer(sample, mime=True)

    @staticmethod
    def resolve_content_encoding(url: str) -> str:
        # Capture from header
        res = requests.head(url, stream=True, timeout=10)
        res.raise_for_status()

        # Grab Header value and evaluate
        header = res.headers.get("Content-Encoding")

        if header not in Utils.STANDARD_CONTENT_ENCODINGS:
            # Check Sample from http request
            # Use extension to determine encoding
            filepath    = urlparse(url).path
            _, ext      = os.path.splitext(filepath)

            # Warn user
            warnings.warn("Unable to resolve Content-Encoding from Headers!")

            # Evaluate resultant .ext
            if not ext:
                return "identity"
            else:
                return ext
            
        # Return result from headers
        else:
            return header

    @staticmethod
    def resolve_content_type(url: str) -> str:
        # Get Content-Type from header and evaluate
        res = requests.head(url, stream=True, timeout=10)
        res.raise_for_status()
        
        # Grab header and evaluate
        # Return if Standard / Reliable Response
        header = res.headers.get("Content-Type", "")
        if header not in Utils.NON_SPECIFIC_CONTENT_TYPES:
            return header
        else:
            # Header non-specific
            # Warn user of missing / improper header for Content-Type
            # Use python-magic with sample extraction
            sample = Utils.get_type_from_sample(url)
            
            # Determine if sample valid
            if sample not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                return sample
            else:
                # Guess using mimetypes
                filepath    = urlparse(url).path
                mimetype, _ = mimetypes.guess_type(filepath)
                
                # Evaluate
                if mimetype not in Utils.NON_SPECIFIC_CONTENT_TYPES:
                    return mimetype
                else:
                    # Return default from Content-Encoding header
                    return header

    @staticmethod
    def resolve_download_directory(base_raw_downloads_dir: Path, source_id: str, timestamp: datetime) -> Path:
        """
        Constructs the target directory path for a raw download and ensures it exists.
        Format: <base_raw_downloads_dir>/<source_id>/<year>/<month>/
        """
        # Check path for objects
        if isinstance(base_raw_downloads_dir, str):
            base_raw_downloads_dir = Path(base_raw_downloads_dir)
        
        # Build Path
        target_dir = base_raw_downloads_dir / source_id / str(timestamp.year) / f"{timestamp.month:02d}"
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    @staticmethod
    def generate_raw_filename(source_id: str, timestamp: datetime, extension: str = ".json.gz", data_version: Optional[str] = None) -> str:
        """
        Generates a standardized raw filename for a downloaded file.
        Format: <source_id>_systems_[vX.Y.Z_]<YYYYMMDD-HHMMSS>.<extension>
        """
        version_str = f"v{data_version}_" if data_version else ""
        timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
        
        # Assuming the 'systems' part is constant for now, based on documentation examples
        filename = f"{source_id}_{version_str}_{timestamp_str}{extension}"
        return filename
