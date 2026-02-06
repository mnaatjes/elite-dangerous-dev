# ETLProcessor Class Schema

This document outlines the proposed class structure for the `ETLProcessor` which is responsible for the v1 data pipeline. This design refactors the procedural script into a more organized, testable, and reusable object-oriented structure.

```python
# ETLProcessor Class Schema

This document outlines the proposed class structure for the `ETLProcessor` which is responsible for the v1 data pipeline. This design refactors the procedural script into a more organized, testable, and reusable object-oriented structure.

```python
import os
import hashlib
import json
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class ETLProcessor:
    """
    Encapsulates the entire ETL process for converting EDSM data into a
    custom binary format for the C++ routing engine.
    """
    # --- Properties ---

    edsm_url: str
    output_dir: Path
    source_id: str
    downloaded_json_gz_path: Path
    decompressed_json_path: Path
    binary_file_path: Path
    checksum_file_path: Path
    processed_count: int
    skipped_count: int

    # --- Initialization ---

    def __init__(self, edsm_url: str, output_dir: str, source_id: str):
        """
        Initializes the ETLProcessor with necessary configuration.

        Args:
            edsm_url: The URL to the EDSM systems data dump.
            output_dir: The directory to store downloaded and processed files.
            source_id: An identifier for the data source (e.g., 'edsm').
        """
        self.edsm_url = edsm_url
        self.output_dir = Path(output_dir)
        self.source_id = source_id

        # Define file paths based on current timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.downloaded_json_gz_path = self.output_dir / "raw" / f"{self.source_id}_{timestamp}.json.gz"
        self.decompressed_json_path = self.output_dir / "raw" / f"{self.source_id}_{timestamp}.json"
        self.binary_file_path = self.output_dir / "bin" / f"{self.source_id}_{timestamp}.bin"
        self.checksum_file_path = self.binary_file_path.with_suffix(".sha256")

        self.processed_count = 0
        self.skipped_count = 0

    # --- Public Methods ---

    def run(self):
        """
        Executes the full ETL pipeline:
        1. Ensures output directory structure exists.
        2. Downloads raw data (json.gz) and verifies its integrity with SHA256.
        3. Decompresses the raw data to a temporary .json file.
        4. Processes records from the temporary JSON to binary, validating each.
        5. Generates a checksum for the final binary file.
        Handles logging for the entire process.
        """
        pass # Implementation will be added

    # --- Private Methods ---

    def _download_data(self):
        """
        Downloads the compressed source data file (`.json.gz`) to a local raw directory.
        After download, it computes its SHA256 hash. If a source-provided checksum
        is available, it verifies the downloaded file's integrity against it.
        """
        pass # Implementation will be added

    def _decompress_data(self):
        """
        Decompresses the locally stored `.json.gz` file into a temporary,
        uncompressed `.json` file.
        """
        pass # Implementation will be added

    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Performs comprehensive validation on a single record from the JSON data.
        Checks for:
        - Presence of required keys (`id64`, `coords`, `x`, `y`, `z`).
        - Correct data types for `id64` and coordinates.
        - Realistic range checks for coordinate values (e.g., galactic bounds).
        Returns True if the record is valid, False otherwise.
        """
        pass # Implementation will be added

    def _process_records(self):
        """
        Reads records from the decompressed `.json` file, validates each using
        `_validate_record()`, packs valid records into a binary format, and writes
        them to the binary output file.
        Updates `self.processed_count` and `self.skipped_count`.
        """
        pass # Implementation will be added

    def _generate_checksum(self):
        """
        Generates a SHA256 checksum for the created binary file
        (`systems_processed.bin`) to ensure data integrity and saves it
        to a `.sha256` file alongside the binary.
        """
        pass # Implementation will be added
``````
