import httpx
import hashlib
from pathlib import Path

from ..base import DownloadStrategy

class GzipRegime(DownloadStrategy):
    def download(self, url: str, destination: Path, client: httpx.Client) -> str:
        sha256 = hashlib.sha256()
        
        with client.stream("GET", url) as response:
            response.raise_for_status()
            
            with open(destination, "wb") as f:
                # Iterate over the response in 128KB chunks
                for chunk in response.iter_bytes(chunk_size=128 * 1024):
                    # Update hash WHILE the data is in memory
                    sha256.update(chunk)
                    # Write to the Linux filesystem
                    f.write(chunk)
                    
        return sha256.hexdigest()