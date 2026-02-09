"""
    Docstring for etl.tests.conftest
"""
import pytest
import json
from pathlib import Path

def load_config():
    config_path = Path("etl/tests")
    with open(Path(config_path / "etl.test.config.json")) as conf:
        return json.load(conf)

@pytest.fixture(scope="session")
def get_conf():
    return load_config()