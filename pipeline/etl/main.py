import os
import pprint
from .config import load_config
from etl import load

"""
Main ETL Pipeline File
    1) Collects configuration
    2) Performs HTTP Requests from defined API Endpoints
    3) Downloads and Decompresses Data
"""
# Constants
PIPELINE_ROOT = os.path.dirname(os.path.dirname(__file__))

def run_etl_pipeline():

    # Check for config file
    config_fp = os.path.join(PIPELINE_ROOT, 'etl.config.json')
    
    # Load Configuration Object from json config file
    config = load_config(config_fp)

    # Notify User
    print(f"Configuration loaded under Name: {config.name}\n")
    print("Beginning download stream...\n")

    # Stream File Download
    load.stream_download("", "", "")
    load.finalize_download("", "")
