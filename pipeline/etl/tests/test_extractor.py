import os
import pytest
from ..src.Extractor import Extractor

"""
    Testing for Extractor Class
"""

ETL_DIR = os.path.abspath("etl/")
OUT_DIR = os.path.join(ETL_DIR, "tests/downloads")
DATA = [
    {"url": "https://downloads.spansh.co.uk/systems_1day.json.gz", "output_dir":OUT_DIR, "expected":True},
    {"url": "http://downloads.spansh.uk/systems.json.tar.gz", "output_dir":OUT_DIR, "expected":False}
]

def test_constructor():
    for obj in DATA:
        test = Extractor(obj["url"], obj["output_dir"])

def test_content_resolution():
    for obj in DATA:
        # Declare Extractor
        extractor = Extractor(obj["url"], obj["output_dir"])

        # Catch Exceptions
        if obj["expected"]:
            extractor.resolve_content_identity()

        else:
            # Catch with pytest
            with pytest.raises(Exception) as exp:
                extractor.resolve_content_identity()
            #print(f"Exception: {exp}")