import pytest
from src.config import settings
from src.persistence import PersistenceManager
from src.adapters import AdapterFactory
# tests/conftest.py

# --- Bootstrapper Method ---
@pytest.fixture(scope="session", autouse=True)
def bootstrap():
    print("\n--- Loading Bootstrap...")
    # 1. Build Adapter
    adapter = AdapterFactory().build_local_filesystem(settings)

    # 2. Get Resolver

    # 3. Build Orchestrator
    pm = PersistenceManager(
        adapter=adapter,
        resolver=
    )