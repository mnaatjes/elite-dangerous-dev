import pytest
from ..src.common.Config import Config
#from ..src.common.Manifest import Manifest

def test_manifest(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()