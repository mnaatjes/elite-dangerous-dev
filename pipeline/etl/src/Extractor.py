import warnings
from .Utils import Utils
from pathlib import Path


"""
    File Extractor Class for ETL Pipeline
    @author Michael Naatjes
    @date 02/06/2026

"""

class Extractor:
    """
    
    """
    # Properties
    url: str
    output_dir: str

    def __init__(self, url, output_dir):
        # Validate & Sanitize URL
        self.url = Utils.sanitize_url(url)
        # Validate Output Directory
        self.output_dir = Utils.validate_path(output_dir, "dir")

    def fetch_data(self, url):
        print(f"Fetching Data...")
