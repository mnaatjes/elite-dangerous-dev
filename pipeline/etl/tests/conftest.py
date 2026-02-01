import pytest
import os
import json
from utils import load_json

@pytest.fixture(scope="session")
def squares_data():
    file_path = os.path.join(os.path.dirname(__file__), 'squares.json')
    return load_json(file_path)

@pytest.fixture(scope="session")
def url_data():
    file_path = os.path.join(os.path.dirname(__file__), 'sample_data/http_data.json')
    return load_json(file_path)