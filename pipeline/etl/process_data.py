# ETL Pipeline Script

import gzip
import ijson
import struct
import requests
import os

# Define the paths relative to the script location
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
BINARY_FILE_PATH = os.path.join(OUTPUT_DIR, 'systems_processed.bin')
EDSM_DUMP_URL = 'https://www.edsm.net/dump/systemsWithCoordinates.json.gz'
EDSM_DUMP_PATH = os.path.join(OUTPUT_DIR, 'systemsWithCoordinates.json.gz')

def download_data():
    """
    Downloads the EDSM data dump if it doesn't already exist.
    """
    print(f"Checking for EDSM data dump at {EDSM_DUMP_PATH}...")
    if not os.path.exists(EDSM_DUMP_PATH):
        print("File not found. Downloading...")
        # NOTE: This downloads the entire file into memory before writing.
        # For very large files, a streaming download approach would be better.
        response = requests.get(EDSM_DUMP_URL, stream=True)
        response.raise_for_status()
        with open(EDSM_DUMP_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    else:
        print("Data dump already exists.")

def process_data():
    """
    Reads the gzipped EDSM JSON dump, extracts the required data,
    and writes it to a compact binary file.
    """
    print(f"Starting data processing from {EDSM_DUMP_PATH}...")
    
    system_count = 0
    with gzip.open(EDSM_DUMP_PATH, 'rt', encoding='utf-8') as f, open(BINARY_FILE_PATH, 'wb') as bin_f:
        # Use ijson to parse the file iteratively
        systems = ijson.items(f, 'item')
        
        for system in systems:
            # Ensure the system has coordinates and an id64
            if 'coords' in system and 'id64' in system:
                id64 = system['id64']
                coords = system['coords']
                x, y, z = coords['x'], coords['y'], coords['z']
                
                # Pack the data into a binary format:
                # - 'q' for long long (8 bytes) for id64
                # - 'd' for double (8 bytes) for each coordinate
                packed_data = struct.pack('qddd', id64, x, y, z)
                bin_f.write(packed_data)
                system_count += 1

    print(f"Processing complete. Wrote {system_count} systems to {BINARY_FILE_PATH}.")

def main():
    """
    Main function to run the ETL pipeline.
    """
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Download the data
    download_data()
    
    # Step 2: Process the data
    process_data()

if __name__ == '__main__':
    main()
