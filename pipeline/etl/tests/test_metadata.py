"""
    Docstring for etl.tests.test_metadata
"""
from datetime import datetime
from pprint import pprint
from pathlib import Path
from ..src.Common.MetaData import MetaData
from ..src.Common.Utils import Utils

def test_new_metadata_instance(get_props, get_files):
    for file in get_files:
        obj = MetaData(file["source_id"], file["url"], get_props["version"])
        

def test_metadata_flow(get_metadata_instance, get_props):
    
    instance = get_metadata_instance
    filepath = Utils.generate_raw_filename(instance.source_id, datetime.now(), ".json.gz", get_props["version"])
    pprint(filepath)

    #instance.save()