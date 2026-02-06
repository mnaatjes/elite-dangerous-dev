from pathlib import Path

"""
    File Download Class for ETL Pipeline
    @author Michael Naatjes
    @date 02/06/2026

"""

class FileDownloader:
    """
    
    """
    # Properties
    url: str
    output_dir: str

    def __init__(self, url, output_dir):
        # Validate and Sanitize
        self.url = self._sanitize_url(url)

        # Validate and return Path object
        self._validate_sys_path(output_dir)
        self.output_dir = Path(output_dir)

    def _sanitize_url(self, url):
        pass

    def _validate_sys_path(self, path):
        pass