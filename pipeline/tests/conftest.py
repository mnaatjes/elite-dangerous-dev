# tests/conftest.py
import pytest
from src.config import settings
from src.adapters import AdapterFactory
from src.gateways import Gateway

@pytest.fixture(scope="session")
def adapter():
    return AdapterFactory().build_local_filesystem(settings)

@pytest.fixture(scope="session")
def gateway(adapter):
    print(Gateway(adapter))