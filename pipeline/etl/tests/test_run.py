"""
Pytest Run Testfile
"""
import os
import pytest
import shutil
import requests
import hashlib
import json
import magic
import psutil
from pathlib import Path
from pprint import pprint
from urllib.parse import urlparse
from datetime import datetime

# --- Constants ---
__CHUNK_MEMORY_SIZES = {
    "1KB": 1024,
    "1MB": 1048576,
    "4MB": 4194304,
    "16MB": 16777216
}

# --- Utility functions ---
def show_memory_status():
    """
    Prints System Memory Status to Console
    Return: Void
    """
    
    print(">> System Memory Resources...")
    memory = psutil.virtual_memory()
    print(f"Total RAM:\t{memory.total / (1024**3):.2f}GB")
    print(f"Available:\t{memory.available / (1024**3):.2f}GB")
    print(f"Used:\t\t{memory.used / (1024**3):.2f}GB")
    print(f"Free:\t\t{memory.free / (1024**3):.2f}GB")
    print(f"In-Use:\t\t{memory.percent}%")

def human_readable_size(size_bytes):
    # Check if string
    if isinstance(size_bytes, str):
        size_bytes = int(size_bytes)

    # Check if 0
    if size_bytes == 0:
        return "0B"
    
    # List of labels
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    
    # The math: log base 1024 of the bytes gives us the index of the unit
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    
    # Equation: size / (1024 ^ i)
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {units[i]}"

def parse_to_bytes(size_str):
    import re
    """
    Converts a human-readable size string (e.g., '1KB', '2.5 GB') to bytes.
    Returns an integer.
    """
    # Normalize input: uppercase and remove spaces
    size_str = size_str.upper().replace(" ", "")
    
    # Regex to capture the number and the unit
    match = re.match(r"^([0-9.]+)([A-Z]{0,2})$", size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
        
    number, unit = match.groups()
    number = float(number)
    
    # Map units to their power of 1024
    # We include 'B' as 0, 'K' or 'KB' as 1, etc.
    units = {
        "": 0, "B": 0,
        "K": 1, "KB": 1,
        "M": 2, "MB": 2,
        "G": 3, "GB": 3,
        "T": 4, "TB": 4,
        "P": 5, "PB": 5
    }
    
    if unit not in units:
        raise ValueError(f"Unknown unit: {unit}")
    
    # The Equation: value * (1024 ** exponent)
    exponent = units[unit]
    return int(number * (1024 ** exponent))

def has_enough_space(destination_dir, content_length_bytes):
    # Get disk stats for the directory where you plan to save the file
    # On Linux, this will check the specific partition the folder sits on
    total, used, free = shutil.disk_usage(destination_dir)
    
    # Check if free space is greater than the file size
    # Pro-tip: Add a "buffer" (e.g., 50MB) so the OS doesn't choke
    buffer = 50 * (1024 ** 2) 

    # Convert content_length into int if string
    if isinstance(content_length_bytes, str):
        content_length_bytes = int(content_length_bytes)
    return free > (content_length_bytes + buffer)

def show_available_disk_space(directory="."):
    """
    Prints the free disk space at a specific directory in a readable format.
    Defaults to the current directory ('.').
    """
    # shutil.disk_usage returns a named tuple (total, used, free) in bytes
    try:
        total, used, free = shutil.disk_usage(directory)
        
        # Convert bytes to Gigabytes for readability
        free_gb = free / (1024 ** 3)
        total_gb = total / (1024 ** 3)
        percent_free = (free / total) * 100

        print(f"Directory:\t{Path(directory).absolute()}")
        print(f"Available:\t{free_gb:.2f} GB")
        print(f"Total Disk:\t{total_gb:.2f} GB")
        print(f"Capacity:\t{percent_free:.1f}% free")
        
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")

def calculate_local_sha256(filename, chunk_size):
    """
    Calculates the SHA-256 hash of an existing local file.
    """
    sha256_hash = hashlib.sha256()
    
    # TODO: Change where try/catch performed
    try:
        with open(filename, "rb") as f:
            # Read the file in 4MB chunks
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    except FileNotFoundError:
        return None

def verify_local_sha256_integrity(filename, expected_hash, chunk_size):
    """
    Re-calculates the hash of an existing file to ensure it 
    hasn't been corrupted or truncated since download.
    """
    print(f"Verifying integrity of {filename}...")
    # Use the streaming hash function we built earlier
    current_hash = calculate_local_sha256(filename, chunk_size)
    
    if current_hash == expected_hash:
        print("Integrity Verified: File is safe to process.")
        return True
    else:
        print("CRITICAL: Local file is corrupted! Hashes do not match.")
        # Logic to delete the corrupted file and trigger a re-download
        return False

def json_serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# --- Extractor Functions ---
def download_binary(chunk_size, filepath, url, original_etag=None):
    # Initiate SHA256 Hash Checksum
    # 1) Duplication Detection
    # 2) Corruption Recovery
    # 3) Data Storage Reference
    sha256 = hashlib.sha256()

    # Create request Stream
    with requests.get(url, stream=True) as res:
        res.raise_for_status()

        # ETag Integrity Verification
        # TODO: Find way of ensuring ALL download_() methods implement
        if original_etag:
            current_etag = res.headers.get("ETag")
            if original_etag != current_etag:
                raise ValueError(
                    f"Integrity Error! Server File changed during session!\n"
                    f"Initial:\t{original_etag}"
                    f"Current:\t{current_etag}"
                )

        # Open and write binary to file
        with open(filepath, "wb") as f:
            # Iterate by chunk
            for chunk in res.iter_content(chunk_size=chunk_size):
                if chunk:
                    # Write file to disk
                    f.write(chunk)
                    # Update SHA256 Hash
                    sha256.update(chunk)
        
        # Return sha256 has checksum
        return sha256.hexdigest()

def verify_file_size(file_path, expected_size_str):
    """
    Compares local file size against the server's Content-Length.
    """
    # TODO: Change exception handling
    try:
        # 1. Convert header string to integer
        expected_size = int(expected_size_str)
        
        # 2. Get the actual size of the file on your Linux drive
        actual_size = os.path.getsize(file_path)
        
        if actual_size == expected_size:
            print(f"Success: File size matches ({actual_size} bytes).")
            return True
        else:
            print(f"Warning: Size mismatch! Local: {actual_size}, Expected: {expected_size}")
            return False
            
    except FileNotFoundError:
        print("Error: Local file not found.")
        return False
    except (ValueError, TypeError):
        print("Error: Invalid expected size provided.")
        return False

# --- Testing Regime ---
def test_flow(get_conf):
    # --- Configuration Properties and Parameters ---
    conf_dict       = get_conf
    conf_downloads  = get_conf["downloads"]
    conf_files      = get_conf["files"]

    conf_downloads_dir = Path(conf_downloads["base_directory"])
    conf_downloads_max_chunk = conf_downloads["max_chunk_size"]
    conf_downloads_strategies = conf_downloads["strategies"]
    conf_ts_format = conf_downloads.get("timestamp_format", "%Y%m%d_%H%M%S%f")
    
    print("\nLoad Config...")
    # TODO: Utils.load_config()
    
    print(">> Configuring Downloads Directory")
    # TODO: Utils.config_downloads_dir()
    if not conf_downloads_dir.exists():
        raise FileNotFoundError(f"Download Directory does NOT exist! {conf_downloads_dir}")
    
    # TODO: Extractor.Manifest.verify()
    print(f">> Checking for Downloads Manifest...")
    manifest_path = Path(conf_downloads_dir / f"manifest_v{conf_dict["version"]}.json")
    if not manifest_path.exists():
        print(f"Creating Manifest File at: {manifest_path}")
        # Create Manifest File
        manifest_init_data = {
                "metadata": {
                    "version": conf_dict.get("version", "unknown"),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": ""
                },
                "downloads": []
            }
        with open(manifest_path, "w") as f:
            json.dump(manifest_init_data, f, indent=4, default=json_serialize)

    # Load Manifest
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    print(" --- Building Metadata...")
    # TODO: Create Metadata Class
    metadata_list = []
    for conf in conf_files:
        # TODO: extract_extension()
        extensions = []
        url_path = urlparse(conf["url"]).path
        url_root, url_ext = os.path.splitext(url_path)
        while url_ext:
            extensions.insert(0, url_ext)
            url_root, url_ext = os.path.splitext(url_root)

            if not url_ext:
                break
            if not url_root:
                break

        # Append Data
        metadata_list.append({
            "source_id": conf["source_id"],
            "label":"systems",
            "url": conf["url"],
            "extensions": extensions,
            "etl_version": conf_dict["version"],
            "file_version": None
        })

    print(" --- Validating URL and File Content...")
    # TODO: fetch_headers()
    for item in metadata_list:
        # Perform Header request
        res = requests.head(item["url"], stream=True, timeout=5)
        res.raise_for_status()

        # Add Metadata
        item["is_valid"]    = True
        item["headers"]     = {
            "response_url":res.url,
            "content_type":res.headers.get("Content-Type", "").lower(),
            "content_encoding":res.headers.get("Content-Encoding", "").lower(),
            "content_length_bytes":res.headers.get("Content-Length", 0),
            "charset":res.encoding,
            "e_tag":res.headers.get("ETag", None),
            "content_md5":res.headers.get("Content-MD5", None),
            "x_sha256":res.headers.get("X-SHA256", None)
        }

    print(" --- Examining Headers...")
    for item in metadata_list:
        headers = item["headers"]

        # TODO: Version Control with ETag
        # Option for checking file version before downloading:
        # 1) Send known e_tag to url with header{'If-None-Match: <ETag>'}
        # 2) Spansh / EDSM will respond with 304 - Not Modified with Zero Payload
        # 3) Means file has not been changed
        # Determine Estimated size of content

        # Check Content-Encoding
        if not headers["content_encoding"]:
            print(f">> WARNING: Content Encoding Missing! for {item["url"]}")

            # Request bytes
            sample = None
            with requests.get(
                url=item["url"],
                headers={"Range":"bytes=0-1023"},
                stream=True,
                timeout=5
            ) as r:
                r.raise_for_status()
                sample = r.raw.read(1024)

            # Perform python-magic check
            if not sample:
                raise ValueError(f"Unable to acquire sample from {item["url"]}")

            mime_type = magic.from_buffer(sample, mime=True)
            print(f">> File from url is {mime_type}")

            # Verify
            if not mime_type:
                raise ValueError(f"Url {item["url"]} did NOT return valide MIME type!")
            # Assign to item
            item["mime_type"] = mime_type
        
    # Extraction / Transformation Decision Matrix
    # 1) MIME Type
    # 2) Content-Type
    # 3) Content-Encoding
    # 4) File Extension
    
    print(" --- Preparing for Download...")
    # Generate timestamp for pathing
    # TODO: Parse directory path information from timestamp
    timestamp = datetime.now()
    year  = str(timestamp.year)
    month = f"{timestamp.month:02}"

    # Loop Metadata entries and perform downloads
    for item in metadata_list:
        # TODO: configure_download_dir()
        # 1) Form path
        # 2) Check for path / create
        destination_dir = Path(conf_downloads_dir / item["source_id"] / year / month)

        if not destination_dir.exists():
            print(f">> Creating Directory at {destination_dir}")
            destination_dir.mkdir(parents=True, exist_ok=True)

        # Prepare for Downloading Process
        # TODO: Determine and Allocate Memory
        # Memory Allocated in Chunks with a max default of 16MB set in etl.config.json

        # Begin Downloading Process
        # TODO: Extractor.download()
        # 1) Determine downloading regime based on metadata properties
        # 2) Sort to appropriate download method for data type
        # 3) Execute download
        # TODO: Extractor.determine_download_strategy()
        item_headers = item.get("headers")
        
        # TODO: Determine disk-space at destination
        if not has_enough_space(destination_dir, item_headers.get("content_length_bytes", 0)):
            raise OSError(f"Not enough disk space available at target directory {destination_dir} for Content-Length (bytes) of {item.get("content_length_bytes")}")

        # Create array of content identity information
        content_identity = [
            item.get("mime_type", None),
            item_headers.get("content_type", None),
            item_headers.get("content_encoding", None),
            item.get("extensions", [])[-1]
        ]

        # Checks for empty values in order of importance
        mime_type = next((i for i in content_identity if i), None)
        if not mime_type:
            raise ValueError(f"Fatal Error: Unable to Determine Mimetype from Metadata given url {item.get("url")}")
        print(f">> MIME Type Determined: {mime_type}")
        download_strategy = conf_downloads_strategies.get(mime_type, None)

        # Store Temp hash
        checksum = None

        # Generate Filenames
        filename = f"{item.get("source_id", "unknown")}_{item.get("label", "generic")}_{timestamp.strftime(conf_ts_format)}{"".join(item.get("extensions"))}"
        filepath = Path(destination_dir / filename)

        # Determine which Download Strategy to Utilize
        match download_strategy:
            # Binary and Default Case
            case "download_binary" | _:
                print(f" --- Performing default strategy: {conf_downloads_strategies.get("default")}()...")
                print(f">> Output Directory: {destination_dir}")
                print(f">> Output Filename: {filename}")
                print(f">> Output Filepath: {filepath}")
                print(f">> File Size: {human_readable_size(item_headers.get("content_length_bytes"))}")
                print(f">> Downloading...")
                
                # Execute Method
                checksum = download_binary(
                    chunk_size=conf_downloads_max_chunk,
                    filepath=filepath,
                    url=item.get("url"),
                    original_etag=item_headers.get("e_tag", "")
                )

        # Verify Download
        # TODO: Checksum
        # 1) Verify Content-Length matches
        is_valid_filesize = verify_file_size(filepath, item_headers.get("content_length_bytes"))
        print(f">> Valid Filesizes: {is_valid_filesize}")

        # 2) Integrity Check with ETag Tracking
        #   a) Store original ETag
        #   b) Compage original ETag with ETag from final GET request
        #   c) Ensures file was not updated/changed during download

        # 3) Sha256 Checksum: Compare existing with new
        print(f">> Checksum sha256: {checksum}")
        is_sha256_valid = verify_local_sha256_integrity(
            filepath,
            checksum,
            conf_downloads_max_chunk
        )
        print(f">> sha256 is: {is_sha256_valid}")

        # 3) Format properties:
        #   a) gzip Trailer: Contains built-in CRC-32 checksum footer
        #   b) Check file is valid gzip
        # TODO: Verify file location
        # TODO: Create metadata JSON compliament file

        print(f">> Download Complete!")

        # TODO: Prepare Manifest and Meta.json data
        manifest_entry = {
            "filename": filename,
            "sha256": checksum,
            "downloaded_at": timestamp.isoformat(),
            "is_valid": is_valid_filesize and is_sha256_valid,
            "size_bytes": item_headers.get("content_length_bytes", 0),
            "source_url": item_headers.get("url"),
            "mime_type": mime_type,
            "e_tag": item_headers.get("e_tag", "")
        }

        # Change updated_at property
        manifest["metadata"]["updated_at"] = timestamp.isoformat()
        # Push to Manifest Dict
        manifest.get("downloads", []).append(manifest_entry)
        # Overwrite Manifest
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4, default=json_serialize)


        # TODO: Extractor.download_gzip()
        # 1) Filename must include .gzip or .json.gzip extension
        # 2) open parameter "wb" (write binary), encoding: None (binary-mode), and iterate content by chunk size


        # TODO: Monitor Disk Space at Download Directory
        