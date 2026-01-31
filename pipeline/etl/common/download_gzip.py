# Function to download and extract qzip file from http response
import datetime
import gzip
import os
from .http_request import make_http_request
from requests.exceptions import RequestException

def download_gzip(url, destination_path):
    """
    Downloads a gzip file from the given URL and extracts its content.

    Args:
        url (str): The URL of the gzip file to download.
        destination_path (str): The file path where the extracted content will be saved.
    
    Returns:
        str: The path to the saved extracted file.
    """

    # Validate destination path
    if not destination_path:
        raise ValueError("Destination path must be provided.")
    
    if os.path.isdir(destination_path):
        raise ValueError("Destination path must be a file path, not a directory.")

    # Form Filepath with timestamp
    ts = datetime.strftime("%Y%m%d_%H%M%S")
    filepath = f"{os.path.splitext(destination_path)[0]}_{ts}.json"
    print(f"Downloading gzip file to: {filepath}")

    if not os.path.exists(os.path.dirname(filepath)):
        raise ValueError("The directory for the destination path does not exist.")

    # Perform HTTP Request and Download the gzip file
    try:
        # Prepare headers
        headers = {
            'Accept-Encoding': 'gzip, json',
            'User-Agent': 'ETL-Downloader/1.0',
            "Content-Encoding": "gzip, json"
        }

        # Make the HTTP request to download the gzip file
        response = make_http_request(url, headers=headers, stream=True)

        # Write the downloaded gzip file to the destination path
        with open(filepath, 'wb') as f_gzip:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f_gzip.write(chunk) # Write the compressed data to file
        
        return filepath
    
    except RequestException as e:
        print(f"An error occurred while downloading the file: {e}")
        return