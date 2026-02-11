"""
Testing for Config Class

"""
from ..src.common.config import Config

def test_include(monkeypatch):
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()
    print(f"Version:\t{conf.version}")
    print(f"Download:\t{conf.downloads.strategies[0].mime_type}")

