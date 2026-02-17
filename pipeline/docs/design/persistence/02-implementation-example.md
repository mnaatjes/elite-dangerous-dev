# Persistence Layer Implementation Example

This document provides a complete, end-to-end Python implementation of the modular persistence layer, demonstrating how the final, decoupled patterns work together.

This example reflects the "clean" architecture where responsibilities are strictly separated:
-   **Adapters** handle infrastructure I/O.
-   **Strategies** handle interchangeable algorithms (serialization, integrity).
-   **Resolvers** handle the logic of selecting which strategies to use.
-   **Factories** handle the assembly of components.
-   **Orchestrators** execute the high-level workflow.

## 1. The Interface Layer (The Contracts)

These abstract base classes define the "rules" for the entire persistence system. They ensure that components are swappable.

```python
# persistence/interfaces/models.py
from typing import NamedTuple, Any, Union
from abc import ABC, abstractmethod

class SerializerStrategy(ABC):
    @abstractmethod
    def serialize(self, data: Any) -> Union[str, bytes]: pass
    @abstractmethod
    def deserialize(self, payload: Union[str, bytes]) -> Any: pass

class IntegrityStrategy(ABC):
    @abstractmethod
    def calculate(self, payload: Union[str, bytes]) -> str: pass
    @abstractmethod
    def validate(self, payload: Union[str, bytes], expected: str) -> bool: pass

class PersistenceProfile(NamedTuple):
    serializer: SerializerStrategy
    integrity: IntegrityStrategy

class AbstractStrategyResolver(ABC):
    @abstractmethod
    def resolve(self, target: str) -> PersistenceProfile: pass

class AbstractAdapter(ABC):
    @abstractmethod
    def write(self, target: str, payload: Union[str, bytes]) -> None: pass
    @abstractmethod
    def exists(self, target: str) -> bool: pass
```

## 2. The Implementation Layer (The Concrete Tools)

This is where the specific logic for a Linux environment and JSON files lives.

```python
# persistence/resolvers/extension.py
import os

class ExtensionStrategyResolver(AbstractStrategyResolver):
    def __init__(self, profiles: dict[str, PersistenceProfile], default: PersistenceProfile):
        self._profiles = profiles
        self._default = default

    def resolve(self, target: str) -> PersistenceProfile:
        _, ext = os.path.splitext(target.lower())
        return self._profiles.get(ext, self._default)

# filesystem/adapters/filesystem.py (Simplified)
class FilesystemAdapter(AbstractAdapter):
    def __init__(self, registry):
        self._registry = registry

    def resolve(self, target: str):
        key, sub = target.lstrip("/").split("/", 1) if "/" in target else (target, "")
        return self._registry.get_anchor(key) / sub

    def write(self, target, payload):
        path = self.resolve(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, bytes): path.write_bytes(payload)
        else: path.write_text(payload, encoding='utf-8')
```

## 3. The Meso Layer (Orchestrator & Factory)

These components coordinate the workflow and assemble the parts.

### The Orchestrator (The Executor)

The "Brain" that manages the workflow but knows nothing about Linux paths or file formats.

```python
# persistence/orchestrator.py
class PersistenceOrchestrator:
    def __init__(self, adapter: AbstractAdapter, profile: PersistenceProfile):
        self._adapter = adapter
        self._serializer = profile.serializer
        self._integrity = profile.integrity

    def save(self, target: str, data: Any) -> str:
        payload = self._serializer.serialize(data)
        checksum = self._integrity.calculate(payload)
        self._adapter.write(target, payload)
        return checksum
```

### The Factory (The Assembler)

The "Knowledge Broker" that ties the Resolver and Adapter together.

```python
# persistence/factories/local.py
class LocalPersistenceFactory:
    def __init__(self, adapter: AbstractAdapter, resolver: AbstractStrategyResolver):
        self._adapter = adapter
        self._resolver = resolver

    def get_orchestrator(self, target: str) -> PersistenceOrchestrator:
        profile = self._resolver.resolve(target)
        return PersistenceOrchestrator(self._adapter, profile)
```

## 4. The Bootstrap Layer (Wiring It All Together)

This script acts as the "God Object" during startup, performing dependency injection to wire the Micro, Meso, and Macro layers together.

```python
# bootstrap.py or main.py
import os
from pathlib import Path

# --- Import components from the project ---
# (Assuming a simplified structure for clarity)
from filesystem.registry import FilesystemRegistry
# from filesystem.adapters.filesystem import FilesystemAdapter
# from persistence.interfaces.models import PersistenceProfile
# from persistence.resolvers.extension import ExtensionStrategyResolver
# from persistence.factories.local import LocalPersistenceFactory
# from persistence.serialization.json import JsonSerializer
# from persistence.integrity.sha256 import Sha256Integrity

def bootstrap_persistence():
    # 1. MOCK: Logic to parse your .ini configuration
    directory_map = {
        "data_root": Path("/srv/elite-dangerous-dev/pipeline/tests/data"),
        "downloads": Path("/srv/elite-dangerous-dev/pipeline/tests/data/downloads"),
        "manifests": Path("/srv/elite-dangerous-dev/pipeline/tests/data/manifests")
    }

    # 2. Initialize Micro-Layer (Infrastructure)
    registry = FilesystemRegistry(directory_map)
    adapter = FilesystemAdapter(registry)

    # 3. Define the Strategy Resolver (Decision Logic)
    profiles = {
        ".json": PersistenceProfile(JsonSerializer(), Sha256Integrity()),
    }
    default_profile = PersistenceProfile(JsonSerializer(), Sha256Integrity())
    resolver = ExtensionStrategyResolver(profiles, default_profile)

    # 4. Initialize Meso-Layer (Factory)
    factory = LocalPersistenceFactory(adapter, resolver)
    
    return factory

# --- Example Execution ---
if __name__ == "__main__":
    # The factory is created once at startup
    factory = bootstrap_persistence()
    
    # --- A high-level service/repository would then use the factory ---
    target_file = "manifests/2026/02/market_data.json"
    file_content = {"status": "active", "systems": 42}
    
    # Get the right tool for the job
    orchestrator = factory.get_orchestrator(target_file)
    
    # Execute the persistence workflow
    checksum = orchestrator.save(target_file, file_content)
    
    print(f"Successfully saved to {target_file} with checksum: {checksum}")
```