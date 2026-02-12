import pytest
from ..src.common.manifests.metadata import ManifestMetadata

def test_manifest_metadata():
    meta = ManifestMetadata(
        root_dir="",
        etl_version="1.0",
        process="downloads"
    )

    meta.touch()
    
    print(meta.to_json())

    meta.sync_stats({"a":{}, "b":{}})

    print(meta.to_json)