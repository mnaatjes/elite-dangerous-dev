import pytest
from ..src.common.Config import Config
#from ..src.common.Manifest import Manifest
from ..src.common.manifest.BaseManifest import BaseManifest
from ..src.common.manifest.schemas.DownloadRecordSchema import DownloadRecordSchema
from ..src.common.manifest.schemas.ManifestSchema import ManifestSchema

def test_manifest(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()

    manifest = BaseManifest(ManifestSchema(
        root_dir=conf.downloads.manifest_directory,
        process="downloads",
        domain="stations",
        etl_version=conf.version,
        record_schema=DownloadRecordSchema
    ))
    print(manifest.data)
    manifest.update("some_filename_38298sfs873dii3j3.json.gz", {
        "filepath":"path/to/file/filename.json.gz",
        "sha256":"33c873c682aa2f516f5a236d122da27c8d4bda4b4cf3aade0dc953ac9d288840",
        "size_bytes":9180948,
        "status":"completed",
        "downloaded_at":"2026-02-09T22:01:33.003383",
        "etag":"9-203940-937sd"
    })