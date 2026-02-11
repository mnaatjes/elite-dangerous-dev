import pytest
from pprint import pprint
from pathlib import Path
from datetime import datetime, timezone
from pydantic import ValidationError

# --- Import Codebase ---
from ..src.common.config import Config
from ..src.common.manifests.manifest import Manifest

# --- Import Schemas and Constants ---
from ..src.common.manifests.schemas.metadata_schema import ManifestMetadataSchema
from ..src.common.manifests.manager import ManifestManager

def test_manifest(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()
    print("Configuration Loaded...")

    ts = datetime.now(timezone.utc)

    manifest = ManifestManager(
        root_dir=Path("/"),
        etl_version=conf.version
    )

    print(manifest.instances)
    manifest.downloads
    print(manifest.downloads.to_json())