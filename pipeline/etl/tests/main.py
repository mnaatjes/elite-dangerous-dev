"""
    Main pytest File
    Utilities: load_json
"""
import os
import pprint
import pytest
from pipeline.etl.common import load_json

# Constants
PARENT_DIR=os.path.dirname(__file__)
ETL_ROOT=os.path.dirname(PARENT_DIR)
PIPELINE_ROOT=os.path.dirname(ETL_ROOT)

# Main Test Run
def test_load_json():
    fp   = os.path.join(PIPELINE_ROOT, 'etl.config.json')
    data = load_json(fp)
    assert isinstance(data, dict)
