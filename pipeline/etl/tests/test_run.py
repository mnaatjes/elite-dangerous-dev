"""
    Test the ETL Process Run
"""
from ..src.common.Config import Config

def test_etl(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf    = Config()
    sources = conf.load_sources()

