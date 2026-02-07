# ETLProcessor Class Schema

This document outlines the class structure for the `ETLProcessor`, which now serves as the orchestrator for the ETL pipeline. It coordinates the activities of the `Extractor`, `Transformer`, and `Loader` components, rather than performing the ETL steps directly. This design promotes modularity, testability, and adherence to the Single Responsibility Principle.

```python
import os
import hashlib
import json
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import the specialized components
from .Extractor import Extractor
from .Transformer import Transformer
from .Loader import Loader
from .MemoryManager import MemoryManager
from ..common.utils import here # Assuming Utils is used for paths/checksums

class ETLProcessor:
    """
    Orchestrates the entire ETL process for converting EDSM data into a
    custom binary format for the C++ routing engine.
    Delegates extraction, transformation, and loading to specialized components.
    """
    # --- Properties ---
    edsm_url: str
    output_dir: Path
    source_id: str
    processed_count: int
    skipped_count: int

    # Injected dependencies
    _extractor: Extractor
    _transformer: Transformer
    _loader: Loader
    _memory_manager: MemoryManager

    # --- Initialization ---

    def __init__(self,
                 edsm_url: str,
                 output_dir: str,
                 source_id: str,
                 extractor: Extractor,
                 transformer: Transformer,
                 loader: Loader,
                 memory_manager: MemoryManager):
        """
        Initializes the ETLProcessor with necessary configuration and its dependencies.

        Args:
            edsm_url: The URL to the EDSM systems data dump.
            output_dir: The directory to store downloaded and processed files.
            source_id: An identifier for the data source (e.g., 'edsm').
            extractor: An instance of the Extractor class.
            transformer: An instance of the Transformer class.
            loader: An instance of the Loader class.
            memory_manager: An instance of the MemoryManager class.
        """
        self.edsm_url = edsm_url
        self.output_dir = Path(output_dir)
        self.source_id = source_id

        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader
        self._memory_manager = memory_manager # Memory limit set on init of MemoryManager

        self.processed_count = 0
        self.skipped_count = 0

    # --- Public Methods ---

    def run(self):
        """
        Executes the full ETL pipeline by coordinating its specialized components.
        1. Configures components (if necessary).
        2. Initiates data extraction via Extractor.
        3. Streams raw data to Transformer for processing (decompression, parsing, validation, packing).
        4. Streams transformed binary data to Loader for writing.
        5. Generates a checksum for the final binary file.
        Handles overall logging and error reporting for the process.
        """
        print(f"ETL Process started for source: {self.source_id}")

        # Example flow (actual implementation would involve streaming data through components)
        # 1. Fetch data stream
        data_stream = self._extractor.fetch_data(self.edsm_url, self.output_dir / "raw")

        # 2. Transform and load data
        # The transformer would yield binary chunks, and the loader would write them
        # This part requires careful coordination for true streaming.

        # For demonstration, assume transformer can process stream and return results or yield
        # For actual streaming, ETLProcessor would iterate over transformer's output
        # and pass to loader.

        # Example simplified call:
        # binary_chunks = self._transformer.transform_stream(data_stream)
        # self._loader.load_data(binary_chunks, self.output_dir / "bin" / f"{self.source_id}.bin")

        # 3. Generate checksum (handled by ETLProcessor or delegated)
        # self._generate_checksum(self.output_dir / "bin" / f"{self.source_id}.bin")

        print(f"ETL Process finished for source: {self.source_id}")

    # --- Private Methods (for orchestration specific tasks) ---

    def _generate_checksum(self, binary_file_path: Path):
        """
        Generates a SHA256 checksum for a given binary file.
        """
        print(f"Generating checksum for {binary_file_path}")
        # Implementation to read file and compute hash
        pass
```
