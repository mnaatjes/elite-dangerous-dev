import requests
from pathlib import Path
from datetime import datetime

def get_bytes(size_str):
    """Converts strings like '5MiB', '1MiB', or '64KiB' to integer bytes."""
    size_str = size_str.upper()
    units = {
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3
    }
    
    # Extract the number and the unit (e.g., '5' and 'MiB')
    for unit, multiplier in units.items():
        if unit in size_str:
            number = float(size_str.replace(unit, "").strip())
            return int(number * multiplier)
    
    return int(size_str) # Fallback if just a raw number string

def download_chunk(url, output_path, size_label):
    # 1. Calculate bytes for the Range header
    total_bytes = get_bytes(size_label)
    # Range is 0-indexed: 0 to (bytes - 1)
    headers = {"Range": f"bytes=0-{total_bytes - 1}"}
    
    print(f"Targeting: {size_label} ({total_bytes} bytes)")

    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        
        # 206 Partial Content is expected for Range requests
        if r.status_code == 206:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved {Path(output_path).stat().st_size} bytes to {output_path}")

# Run it
ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
URL = "https://downloads.spansh.co.uk/systems_1day.json.gz"
DOWNLOAD_SIZE = "16KB" 
ROOT_DIR = "/srv/elite-dangerous-dev/pipeline/etl/tests/dummy_data/"
download_chunk(URL, f"{ROOT_DIR}test_data_{ts}.gz", DOWNLOAD_SIZE)