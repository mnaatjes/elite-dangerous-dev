import requests
import gzip
import shutil
from pathlib import Path
from datetime import datetime

def download_decompressed_segment(url, output_path, mib_limit=1):
    """
    Downloads a gzipped file, decompresses it on the fly, 
    and saves exactly the first X MiB as a text file.
    """
    # 1. Setup paths and limits
    target_file = Path(output_path)
    limit_in_bytes = mib_limit * 1024 * 1024
    bytes_written = 0

    print(f"Connecting to: {url}")
    
    # 2. Open the stream (stream=True is critical for large files)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        
        # 3. Use GzipFile to decompress the raw stream as it arrives
        # We use r.raw because it provides the binary socket handle
        with gzip.GzipFile(fileobj=r.raw) as decompressor:
            
            # 4. Open local file in 'w' (text) mode
            with open(target_file, "w", encoding="utf-8") as f_out:
                print(f"Decompressing and saving {mib_limit}MiB...")
                
                # Process in small 8KB chunks for memory efficiency
                for chunk in decompressor:
                    # Decode the binary chunk to string (UTF-8)
                    decoded_chunk = chunk.decode('utf-8', errors='ignore')
                    
                    # Calculate how much we can write before hitting the limit
                    remaining_budget = limit_in_bytes - bytes_written
                    
                    if len(decoded_chunk.encode('utf-8')) >= remaining_budget:
                        # Write only what remains of our budget and stop
                        f_out.write(decoded_chunk[:remaining_budget])
                        break
                    
                    f_out.write(decoded_chunk)
                    bytes_written += len(decoded_chunk.encode('utf-8'))
                    
    print(f"Successfully saved {target_file.stat().st_size / (1024*1024):.2f} MiB to {target_file}")

# --- CONFIGURATION ---
# Use your GitHub Raw link or EDSM/Spansh .json.gz link here
ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
URL      = "https://downloads.spansh.co.uk/systems_1week.json.gz"
ROOT_DIR = "/srv/elite-dangerous-dev/pipeline/etl/tests/dummy_data/"
OUTPUT   = f"{ROOT_DIR}spansh_{ts}.json"

if __name__ == "__main__":
    download_decompressed_segment(URL, OUTPUT, 1)