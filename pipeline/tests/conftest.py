# tests/conftest.py
import pytest
from src.config import settings
from src.adapters.factory import AdapterFactory
from src.persistence.strategies.library import StrategyLibrary
from src.persistence.strategies.const import Capability, Category
from src.persistence import PersistenceManager
# --- Serializers and Integrity Strategies ---
from src.persistence.strategies.serialization import AtomicBinarySerializer, AtomicJSONSerializer
from src.persistence.strategies.integrity import AtomicSha256Strategy, NoOpIntegrity

# --- Bootstrapper Method ---
@pytest.fixture(scope="session", autouse=True)
def bootstrap():
    print("\n--- Loading Bootstrap...")
    # 1. Build Adapter
    adapter = AdapterFactory().build_local_filesystem(settings)

    # Get Persistence Manger
    pm = PersistenceManager(adapter=adapter)

    
    manifest = pm.lib.find(
        category=Category.SERIALIZER,
        required_capabilities=Capability.STREAM
    )

    print(f"Manifest: {manifest}")

    for i in pm.lib.list_all():
        print(f"\t --- {i}\n")
    