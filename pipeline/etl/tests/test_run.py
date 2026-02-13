"""
    Test the ETL Process Run
"""
# --- Imports: Libraries ---
from ..src.common.config import Config
from pathlib import Path
from pprint import pprint

# --- Imports: Sourcecode ---
from ..src.common.manifests.manager import ManifestManager

def test_etl(monkeypatch):

    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf    = Config()
    sources = conf.load_sources()

    # --- Main Configuration Properties ---
    conf_downloads_dir  = Path(conf.downloads.base_directory)
    conf_strategies     = conf.downloads.strategies
    conf_max_chunk_size = conf.downloads.max_chunk_size
    conf_ts_format      = conf.downloads.timestamp_format

    # TODO: Refactor Source management and create appropriate classes
    # TODO: Determine which Class / Obj this is part of
    # Validate Downloads Path
    if not conf_downloads_dir.exists():
        raise FileNotFoundError(f"Base Downloads Directory: {conf_downloads_dir} does NOT exist!")
    
    # TODO: Implement a UUID for each specific execution

    # --- Manifest Initialization | Orchestration ---
    manifest = ManifestManager(
        root_dir="etl/tests/manifests",
        etl_version=conf.version
    )
    
    # Initialize Downloads Manifest
    manifest.downloads
    pprint(manifest.instances)

    # TODO: Metadata Orchestration
    # 1) Determine properties
    # 2) Validate target directory
    # 3) Determine parameters (ts_downloads, source_props, checksum_props)
    # 4) Determine how to assemble metadata and what to pull from requests.head(...)
    # 5) Determine filepath and filename

    # TODO: Downloads Orchestration
    # 1) MIME Type Collection / Validation of Content Identity / Decision Tree
    # 2) Implementation of Checksums: sha256, ETag, content_length
    # 3) Versioning and Version Control for incoming files from Sources
    # 4) Development of various download methods based on conf.downloads.strategies
    # 5) Performing Downloads
    # 6) Verifying Data and Version
    # 7) Writing metadata.json files and updating manifest.json
    # 8) Cleanup
