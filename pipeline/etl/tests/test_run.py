import pytest
import json
from pathlib import Path
from pprint import pprint
"""
    Docstring for etl.tests.test_run

"""
def _test_load(get_props):
    pprint(get_props)

def _test_file(get_files):
    for obj in get_files:
        print(obj["url"])

