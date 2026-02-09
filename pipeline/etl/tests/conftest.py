import pytest
import json
from pathlib import Path
from pprint import pprint
from ..src.Common.MetaData import MetaData
"""
    Conftest.py

"""

def load_config():
    curr_dir = Path(__file__).parent
    config_path = Path(curr_dir, "etl.test.config.json")
    
    if not config_path.exists():
        raise FileNotFoundError(f" Cannot find Config File at {config_path}")

    with open(config_path, 'r') as f:
        return json.load(f)

@pytest.fixture(scope="session")
def get_files():
    return load_config()["etl"]["files"]

@pytest.fixture(scope="session")
def get_props():
    conf = load_config()["etl"]
    return {
        "version": conf["version"],
        "root_dir": conf["root_dir"],
        "base_download_path": conf["base_download_path"]
    }

@pytest.fixture(scope="session")
def get_metadata_instance():
    conf = load_config()["etl"]
    file = conf["files"][0]
    return MetaData(file["source_id"], file["url"], conf["version"])