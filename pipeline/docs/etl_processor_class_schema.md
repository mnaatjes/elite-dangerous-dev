# ETLProcessor Class Schema

This document outlines the proposed class structure for the `ETLProcessor` which is responsible for the v1 data pipeline. This design refactors the procedural script into a more organized, testable, and reusable object-oriented structure.

```python
import os
from typing import Dict, Any

class ETLProcessor:
    """
    Encapsulates the entire ETL process for converting EDSM data into a
    custom binary format for the C++ routing engine.
    """
    # --- Properties ---

    edsm_url: str
    output_dir: str
    raw_data_path: str
    binary_file_path: str
    checksum_file_path: str
    processed_count: int
    skipped_count: int

    # --- Initialization ---

    def __init__(self, edsm_url: str, output_dir: str):
        """
        Initializes the ETLProcessor with necessary configuration.

        Args:
            edsm_url: The URL to the EDSM systems data dump.
            output_dir: The directory to store downloaded and processed files.
        """
        self.edsm_url = edsm_url
        self.output_dir = output_dir
        self.raw_data_path = os.path.join(self.output_dir, 'systemsWithCoordinates.json.gz')
        self.binary_file_path = os.path.join(self.output_dir, 'systems_processed.bin')
        self.checksum_file_path = f"{self.binary_file_path}.sha256"

        self.processed_count = 0
        self.skipped_count = 0

    # --- Public Methods ---

    def run(self):
        """
        Executes the full ETL pipeline:
        1. Ensures output directory exists.
        2. Downloads data if needed.
        3. Processes records from JSON to binary.
        4. Generates a checksum for the binary file (if records were processed).
        Handles logging for the entire process.
        """
        pass

    # --- Private Methods ---

    def _download_data(self):
        """
        Downloads the source data file if it doesn't exist locally.
        Uses a streaming download to handle large files efficiently.
        """
        pass

    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Performs validation on a single record from the JSON data.
        Returns True if the record is valid, False otherwise.
        """
        pass

    def _process_records(self):
        """
        Reads the gzipped JSON, validates each record, and writes valid
        records to the binary output file.
        Updates self.processed_count and self.skipped_count.
        """
        pass

    def _generate_checksum(self):
        """
        Generates a SHA256 checksum for the created binary file to ensure
        data integrity and saves it to a .sha256 file.
        """
        pass
```
