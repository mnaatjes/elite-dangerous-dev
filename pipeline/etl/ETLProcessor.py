"""
Main ETL Class for the entire ETL process for converting EDSM and Spansh data into custom binary format for C++ routing engine

"""
import os
import ijson
import requests
import pprint
import gzip
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

    def __init__(self, url, output_dir, source_id):
        """
        Initialize Class

        Args:
            url: [str] URL for data
        """

        self.url            = url
        self.output_dir     = Path(output_dir)
        self.source_id      = source_id
    

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
            "bin": base_path / "bin"
        }

        # Verify Paths exist / Make them
        for p in self.output_paths.values():
            p.mkdir(parents=False, exist_ok=True)


    def _stream_data(self):
        """
            Performs Download of file stream
            1) Makes GET request
            2) Checks for content-encoding
            3) Decompresses zipped content
            4) Stores in output dir
        """
        # Define Output Filenames
        # Generate Timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_bin = self.output_paths["bin"] / f"{self.source_id.lower()}_{ts}.bin"
        output_raw = self.output_paths["raw"] / f"{self.source_id.lower()}_{ts}.json"

        # Perform Context Managed Request
        with requests.get(self.url, stream=True) as res:
            # Raise Errors
            res.raise_for_status()
            
            # Open Binary Output File
            with open(output_bin, 'wb') as f_bin:
                # Ensure Content Type is application/json
                if 'application/json' in res.headers.get('Content-Type', ''):
                    # Check Content Encoding for gzip Compression
                    if 'gzip' in res.headers.get('Content-Encoding', '').lower():
                        # Decompress Raw Data Stream
                        unzipped    = gzip.GzipFile(fileobj=res.raw, mode='rb')
                        json_stream = unzipped
                    else:
                        json_stream = res.raw
                else:
                    raise TypeError(f"Invalid Content-Type for incoming data! Content-Type: {res.headers.get('Content-Type')}")
                
                # Feed Stream into iJSON.items
                for obj in ijson.items(json_stream, ''):
                    # TODO: Perform object validation
                    # TODO: e.g. if not isinstance(obj, dict): {...} | if 'id64' not in obj

                    # Define Properties
                    id64 = obj.get('id64')
                    
