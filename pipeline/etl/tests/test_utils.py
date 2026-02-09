import pytest
import os
import json
import mimetypes
from pathlib import Path
from ..src.Common.Utils import Utils
"""
    Utility Class Tester
"""
DATA_DIR = os.path.abspath('etl/tests/data/')
DATA = [
    {"url": "https://downloads.spansh.co.uk/systems_1day.json.gz", "expected":True},
    {"url": "http://www.failure.com/filenotfound.xml", "expected":True},
    {"url": "http://wikipedia.org", "expected":False}
]
# Load JSON Data
def load_urls(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

url_data = load_urls("test_urls.json")
@pytest.mark.parametrize("item", url_data)
def test_sanitize_url(item):
    #print(item["url"])

    url             = item["url"]
    expected_valid  = item["expected_valid"]
    description     = item["description"] # Using description for clearer messages

    if expected_valid:
        # Expecting a valid URL, so sanitize_url should not raise an error
        try:
            sanitized_url = Utils.sanitize_url(url)
            # You can add more assertions here if needed, e.g., checking return value structure
            assert isinstance(sanitized_url, str) and len(sanitized_url) > 0
        except ValueError as e:
            pytest.fail(f"Valid URL '{url}' ({description}) unexpectedly raised ValueError: {e}")
    else:
        # Expecting an invalid URL, so sanitize_url should raise a ValueError
        with pytest.raises(ValueError) as excinfo:
            Utils.sanitize_url(url)
        # Assert that the error message contains one of the expected invalid reasons
        assert "Invalid URL format" in str(excinfo.value) or \
               "Unsupported URL scheme" in str(excinfo.value) or \
               "Invalid hostname" in str(excinfo.value), \
               f"Invalid URL '{url}' ({description}) raised unexpected error: {excinfo.value}"

def some_err(n):
    if n < 10:
        raise ValueError(f"Value {n} is TOO LOW!")

def test_raises():
    data = {
        "value": 5,
        "expected": False,
        "desc": "Value is below target of 10"
    }
    #print("Testing exception catching...\n")

    if data["expected"] == False:
        with pytest.raises(ValueError) as excinfo:
            some_err(data["value"])
        assert data["expected"] == False
        assert excinfo.type is ValueError
        
def test_validate_path():
    data = [
        {"path": "/srv/elite-dangerous-dev/pipeline/etl", "type":"dir", "expected": True},
        {"path": os.path.join(DATA_DIR, 'test_urls.json'), "type":"file", "expected": True},
        {"path": "etl/", "type":"dir", "expected": True},
        {"path": "etl/tests/data", "type":"dir", "expected": True},
        {"path": "etl/src/", "type":"dir", "expected": True},
        {"path": "/", "type":"dir", "expected": True}
    ]

    for obj in data:
        if obj["expected"]:
            result = Utils.validate_path(obj["path"], obj["type"])
            assert isinstance(result, Path)
        else:
            with pytest.raises(ValueError) as exp:
                Utils.validate_path(obj["path"])
            assert exp.type is ValueError

def test_content_type():
    data = [
        {"url": "https://downloads.spansh.co.uk/systems_1day.json.gz", "expected":True}
    ]
    
    for obj in data:
        if obj["expected"]:
            headers = Utils.get_content_headers(obj["url"])
            mimes = Utils.guess_url_mime_type(obj["url"])
            #print(f"Content-Type: {headers["Content-Type"]}, Content-Encoding: {headers["Content-Encoding"]}")
            #print(f"Content-Type: {headers["Content-Type"]}, {mimes["Content-Type"]}")
            #print(f"Content-Encoding: {headers["Content-Encoding"]}, {mimes["Content-Encoding"]}")

def test_url_get_ext():
    data = [
        {"url": "https://downloads.spansh.co.uk/systems_1day.json.gz", "expected":True},
        {"url": "http://downloads.spansh.uk/systems.json.tar.gz"}
    ]

    for obj in data:
        result = Utils.get_url_extensions(obj["url"])
        #print(result)

def test_sample():
    data = [
        {"url": "https://downloads.spansh.co.uk/systems_1day.json.gz", "expected":True},
        {"url": "http://www.failure.com/filenotfound.xml"}
    ]

    for obj in data:
        Utils.get_type_from_sample(obj["url"])

def test_encoding():

    # Loop and test
    for obj in DATA:
        result = Utils.resolve_content_encoding(obj["url"])
        #print(result)

def test_content_type_resolution():
    for obj in DATA:
        if obj["expected"]:
            result = Utils.resolve_content_type(obj["url"])
            print(result)