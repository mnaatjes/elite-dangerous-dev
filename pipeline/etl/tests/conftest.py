import pytest
import os
import json

# Helper - Load Destination Test Data from JSON file
def load_json(filename):
    fp = os.path.join(os.path.dirname(__file__), 'sample_data', filename)

    with open(fp, 'r') as file:
        data = json.load(file)
    return data

# Load Test URL Data
@pytest.fixture(scope="session")
def load_url_data():
    return load_json("url_test_cases.json")