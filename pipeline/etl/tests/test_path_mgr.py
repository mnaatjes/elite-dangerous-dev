#import pytest
from ..src.config.model import ETLConfig
from ..src.common.path_manager import PathManager
from ..src.common.manifests.manager import ManifestManager

def test_path_manager():
    conf = ETLConfig()
    fm = PathManager(config=conf)

    manifest_mgr = ManifestManager(fm.get_manifests_dir(), conf.version)

    manifest = manifest_mgr.downloads
    test_case = manifest.load()
    print(test_case)
