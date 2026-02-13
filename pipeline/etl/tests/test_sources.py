
import os
import pytest
from pprint import pprint
from pathlib import Path
from ..src.extractor.sources.source_manager import SourcesManager

def test_sources(monkeypatch):

    # --- Load Configurations ---
    monkeypatch.setenv("ETL_SOURCE_PATH", "etl/tests/etl.sources.json")

    source_path = Path(os.getenv("ETL_SOURCE_PATH", ""))
    if not source_path.exists():
        raise FileNotFoundError(f"Cannot find Configuration File at {source_path}")
    
    source_manager = SourcesManager(source_path)
    
    for s in source_manager.get_all():
        print(f"Source: {s.source_id}, {s.connection.url}, {s.dataset}")
    
    print(source_manager.get_source("spansh"))