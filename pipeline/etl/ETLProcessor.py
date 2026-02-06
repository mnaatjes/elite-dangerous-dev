"""
Main ETL Class for the entire ETL process for converting EDSM and Spansh data into custom binary format for C++ routing engine

"""


import os
import io
import ijson
import json
import requests
import pprint
import struct
import gzip
import psutil
import resource
from datetime import datetime
from pathlib import Path

from .common.utils import here

class ETLProcessor:
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    # --- Properties ---
    url: str
    output_dir: str
    source_id: str
    output_paths: dict
    processed: int
    skipped: int
    _total_ram: int
    _memory_perc: int
    _memory_limit: float

    def __init__(self, url, output_dir, source_id, memory_percentage=0.75):
        """
        Initialize Class

        Args:
            url: [str] URL for data
        """

        self.url            = url
        self.output_dir     = Path(output_dir)
        self.source_id      = source_id
        self.skipped        = 0
        self.processed      = 0

        # Set memory limit
        self._set_memory_limit(memory_percentage)

    # --- Public Methods
    def run(self):
        """
            Executes full ELT Pipeline
            1) Ensures output dir exists
            2) Downloads data
            3) Processes records from JSON to Binary
            4) Generates checksum for binary file - if data processed
        """

        # Validate URL
        self._validateURL()

        # Validate Output Path
        if not self.output_dir.is_dir():
            raise TypeError(f"Provided 'output_dir' is NOT a directory: {self.output_dir}")
        
        # Define Raw and Bin output paths
        self._define_output_paths()
        
        # Perform Data Download / Stream / Conversion
        
    def _validateURL(self):
        """
            Ensures Provided URL:
            1) Ensure not empty
            2) Begins with 'http' or 'https'
            3) Content-Type is application/json
        """
        #Empty string
        if not self.url:
            raise ValueError(f"URL String Empty!")
        # Missing http:// or https://
        if not self.url.startswith(("http://", "https://")):
            raise ValueError(f"URL string missing 'http://' or 'https://' in url: {self.url}")
        
    def _define_output_paths(self):
        # grab base path
        base_path = self.output_dir.resolve()

        # Create Output Path Dict
        self.output_paths = {
            "raw": base_path / "raw",
            "bin": base_path / "bin",
            "tmp": base_path / "tmp"
        }

        # Verify Paths exist / Make them
        for p in self.output_paths.values():
            p.mkdir(parents=False, exist_ok=True)

    def _download_gzip(self):
        # Define Output Filename for output/raw
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_raw = self.output_paths["raw"] / f"{self.source_id.lower()}_{ts}.json"

        # Perform HTTP Request via Context Manager
        # Perform Context Managed Request
        with requests.get(self.url, stream=True) as res:
            # Raise Errors
            res.raise_for_status()

            # Open/Create output file and begin to write
            with open(output_raw, 'w', encoding='utf-8') as file_raw:

                # Stream from URL directly to gzip
                with gzip.GzipFile(fileobj=res.raw) as stream_gz:
                    # Parse bytes into Python Dict
                    for line in stream_gz:
                        # Capture Data
                        data = json.loads(line)
                        # Determine if list or NDJSON
                        if isinstance(data, list):
                            for item in data:
                                file_raw.write(json.dumps(item) + "\n")
                        else:
                            #NDJSON
                            file_raw.write(json.dumps(data) + "\n")

        # Stream Complete
        print(f"Filestream Complete: Saved to {output_raw}")

    def _set_memory_limit(self, percentage):
        # Get system ram
        total_ram = psutil.virtual_memory().total
        # Set Resource Usage
        limit = int(total_ram * percentage)
        # Apply resource limit
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

        #Log Memory Change
        # TODO: Add to logger
        #print(f"Memory Limit set to {limit // (1024**2)}MB")