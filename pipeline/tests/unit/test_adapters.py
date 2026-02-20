# tests/unit/test_adapters.py
from src.config import settings
from src.adapters import AdapterFactory

def test_build():
    adapter = AdapterFactory().build_local_filesystem(settings)