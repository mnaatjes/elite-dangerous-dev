"""
    Testing Main Script
"""
import pytest
import json
import os
import sys
import pprint
from pathlib import Path

from ..common.utils import here
from ..ETLProcessor import ETLProcessor

# Constants
OUTPUT_DIR  = "etl/tests/output"
URL         = "https://jsonplaceholder.typicode.com/posts/1"
SOURCE_ID   = "edsm"

# load test data
with open('etl/tests/data/urls.json') as f:
    URL_DATA = json.load(f)

# Test _validateURL
@pytest.mark.parametrize('item', URL_DATA)
def test_validate_url(item):
    # Run verification
    obj = ETLProcessor(item['url'], OUTPUT_DIR, SOURCE_ID)
    #Check valid for raise exception
    if item['expected_valid']:
        obj._validateURL()
    else:
        # Raise ValueError
        with pytest.raises(ValueError) as excinfo:
            obj._validateURL()
        assert item['url'] in str(excinfo.value)
        #print(excinfo)

def test_define_paths():
    obj = ETLProcessor(URL, OUTPUT_DIR, SOURCE_ID)
    obj._define_output_paths()

