import pytest
import os
from datetime import datetime, timezone
from ..src.config.model import ETLConfig
from ..src.manifest.manager import ManifestManager
from ..src.common.path_manager import PathManager
from ..src.manifest.record import Record as ManifestRecord

def test_path_manager():
    conf = ETLConfig()
    pm = PathManager(config=conf)
    manifest_mgr = ManifestManager(
        path_manager=pm,
        config=conf
    )

    downloads_manifest = manifest_mgr.load("downloads", conf.version)