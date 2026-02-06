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
#URL         = "https://data.gharchive.org/2024-01-01-15.json.gz" # 500MiB
#URL         = "https://wiki.mozilla.org/images/f/ff/Example.json.gz" #1KiB
URL         = "https://github.com/mnaatjes/elite-dangerous-dev/raw/refs/heads/feat/etl-pipeline/pipeline/etl/tests/dummy_data/20260206_195716.json.gz"
SOURCE_ID   = "edsm"
MEMORY_PERC = 0.75

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

def test_download_gzip():
    obj = ETLProcessor(URL, OUTPUT_DIR, SOURCE_ID)
    obj._define_output_paths()
    obj._download_gzip()


