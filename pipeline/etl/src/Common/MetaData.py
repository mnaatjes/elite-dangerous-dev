# etl/src/Common/MetaData.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class MetaData:
    """
    A class to encapsulate and manage all metadata associated with a single ETL pipeline run,
    from raw data download to processed binary output.
    """

    def __init__(self,
                 source_id: str,
                 original_url: str,
                 pipeline_version: str):
        """
        Initializes a new MetaData object.

        Args:
            source_id: A unique identifier for the data source (e.g., 'edsm', 'spansh').
            original_url: The full URL from which the raw data was originally downloaded.
            pipeline_version: The version of the ETL pipeline code that performed this run.
        """
        # Properties passed directly during initialization
        self.source_id = source_id
        self.original_url = original_url
        self.pipeline_version = pipeline_version

        # Properties not passed during initialization, set with default values
        self.download_timestamp_utc: Optional[datetime] = None
        self.raw_file_path: Optional[Path] = None
        self.raw_file_size_bytes: Optional[int] = None
        self.raw_file_sha256_checksum: Optional[str] = None

        self.processed_binary_path: Optional[Path] = None
        self.processed_binary_sha256_checksum: Optional[str] = None
        self.processed_count: int = 0
        self.skipped_count: int = 0
        self.source_data_version: Optional[str] = None # Will be populated by Extractor if available

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the MetaData object's properties into a dictionary suitable for JSON serialization.
        Path and datetime objects are converted to string representations.
        """
        data = {
            "source_id": self.source_id,
            "original_url": self.original_url,
            "pipeline_version": self.pipeline_version,
            "download_timestamp_utc": self.download_timestamp_utc.isoformat() if self.download_timestamp_utc else None,
            "raw_file_path": str(self.raw_file_path) if self.raw_file_path else None,
            "raw_file_size_bytes": self.raw_file_size_bytes,
            "raw_file_sha256_checksum": self.raw_file_sha256_checksum,
            "processed_binary_path": str(self.processed_binary_path) if self.processed_binary_path else None,
            "processed_binary_sha256_checksum": self.processed_binary_sha256_checksum,
            "processed_count": self.processed_count,
            "skipped_count": self.skipped_count,
            "source_data_version": self.source_data_version,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Creates a MetaData object from a dictionary (e.g., loaded from a JSON file).
        String representations are converted back to Path and datetime objects.
        """
        # Initialize with required parameters first
        instance = cls(
            source_id=data["source_id"],
            original_url=data["original_url"],
            pipeline_version=data["pipeline_version"]
        )

        # Populate other attributes, handling None values and type conversions
        instance.download_timestamp_utc = datetime.fromisoformat(data["download_timestamp_utc"]) if data.get("download_timestamp_utc") else None
        instance.raw_file_path = Path(data["raw_file_path"]) if data.get("raw_file_path") else None
        instance.raw_file_size_bytes = data.get("raw_file_size_bytes")
        instance.raw_file_sha256_checksum = data.get("raw_file_sha256_checksum")

        instance.processed_binary_path = Path(data["processed_binary_path"]) if data.get("processed_binary_path") else None
        instance.processed_binary_sha256_checksum = data.get("processed_binary_sha256_checksum")
        instance.processed_count = data.get("processed_count", 0)
        instance.skipped_count = data.get("skipped_count", 0)
        instance.source_data_version = data.get("source_data_version")

        return instance

    def save(self) -> Path:
        """
        Serializes the MetaData object to a uniquely named JSON file
        in the same directory as its raw_file_path.
        The filename will be derived from the raw_file_path's name with a '.meta.json' suffix.

        Returns:
            The Path object to the newly created meta.json file.
        """
        if not self.raw_file_path:
            raise ValueError("Cannot save MetaData: raw_file_path is not set.")

        # Ensure the directory for the raw file exists (it should, but good practice)
        self.raw_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Construct the meta.json file path based on the raw file path
        # Example: if raw_file_path is /path/to/data.json.gz
        # meta_json_path will be /path/to/data.json.gz.meta.json
        meta_json_path = self.raw_file_path.parent / f"{self.raw_file_path.name}.meta.json"

        with open(meta_json_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        return meta_json_path

    @classmethod
    def load(cls, meta_json_path: Path):
        """
        Loads metadata from a specific uniquely named meta.json file and creates a MetaData object.
        The `meta_json_path` must point directly to the meta.json file (e.g., /path/to/data.json.gz.meta.json).
        """
        if not meta_json_path.is_file():
            raise FileNotFoundError(f"Metadata file not found: {meta_json_path}")

        with open(meta_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)