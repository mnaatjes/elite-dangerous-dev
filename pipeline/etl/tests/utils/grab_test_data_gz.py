import requests
from pathlib import Path

def download_compressed_chunk(url, output_path, mib_limit=5):
    """
    Downloads a 5MiB binary chunk of a remote file without decompressing.
    The resulting file will be a valid gzip segment (though truncated).
    """
    # 1. Calculate the byte range (0 to 5MiB - 1)
    # Range is inclusive: 0-5242879 is exactly 5,242,880 bytes
    limit_in_bytes = (mib_limit * 1024 * 1024) - 1
    headers = {"Range": f"bytes=0-{limit_in_bytes}"}

    # 2. Ensure the output path is a Path object
    output_file = Path(output_path)
    
    print(f"Connecting to: {url}")
    print(f"Requesting range: {headers['Range']}")

    # 3. Use stream=True to handle the binary transfer efficiently
    with requests.get(url, headers=headers, stream=True) as r:
        # HTTP 206 is the standard response for Partial Content
        if r.status_code == 206:
            # We use 'wb' (Write Binary) because we are not decompressing
            with open(output_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            actual_size = output_file.stat().st_size
            print(f"Success! Saved {actual_size} bytes to {output_file}")
        
        elif r.status_code == 200:
            print("Warning: Server ignored Range header and sent the whole file.")
            # Depending on your needs, you might want to stop here or save it.
        else:
            print(f"Error: Server returned status {r.status_code}")

# --- CONFIGURATION ---
# Use the .json.gz URL from EDSM, Spansh, or your repository
URL = "https://downloads.spansh.co.uk/systems_1week.json.gz"
# Note: Use .gz extension so Linux/VSCode knows what it is
OUTPUT = "test_data_chunk.json.gz"

if __name__ == "__main__":
    download_compressed_chunk(URL, OUTPUT)