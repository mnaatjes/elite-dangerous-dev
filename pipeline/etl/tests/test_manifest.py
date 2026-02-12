import pytest
from pprint import pprint
from pathlib import Path
from datetime import datetime, timezone
from pydantic import ValidationError

# --- Import Codebase ---
from ..src.common.config import Config
from ..src.common.manifests.manifest import Manifest
from ..src.common.manifests.manager import ManifestManager

def test_manifest(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()
    print("Configuration Loaded...")

    ts = datetime.now(timezone.utc)

    manifest = ManifestManager(
        root_dir=Path("etl/tests/manifests/"),
        etl_version=conf.version
    )

    manifest.downloads
    manifest.validation
    print(manifest.instances)

    # 1. Prepare your raw dictionary from the downloader logic
    new_file_data = {
        "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "filename": "stations_data.json.gz",
        "filepath": "/data/raw/stations_data.json.gz",
        "content_length_bytes": 1048576,
        "status": "completed"
    }

    # 2. Trigger the orchestration
    manifest.downloads.add_record(new_file_data)

    pprint(manifest.downloads.inspect())

