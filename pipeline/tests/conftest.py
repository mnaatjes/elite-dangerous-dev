# tests/conftest.py
import pytest

from src.config import settings
from src.core import SystemMonitor, DataMeasurer
from src.adapters.factory import AdapterFactory
from src.persistence.strategies.library import StrategyLibrary
from src.persistence.strategies.const import Capability, Category
from src.persistence import PersistenceManager
# --- Serializers and Integrity Strategies ---
from src.persistence.strategies.serialization import AtomicBinarySerializer, AtomicJSONSerializer
from src.persistence.strategies.integrity import AtomicSha256Strategy, NoOpIntegrity

# --- Bootstrapper Method ---
@pytest.fixture(scope="session", autouse=True)
def adapter():
    return AdapterFactory().build_local_filesystem(settings)
@pytest.fixture(scope="session", autouse=True)
def manager(adapter):
    return PersistenceManager(adapter=adapter)
    