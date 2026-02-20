# tests/conftest.py
import pytest
from src.config import settings
from src.adapters import AdapterFactory

@pytest.fixture(scope="session")
def adapter():
    return AdapterFactory().build_local_filesystem(settings)