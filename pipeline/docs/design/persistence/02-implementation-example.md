# Persistence Layer Implementation Example

This document provides a complete, end-to-end Python implementation of the modular persistence layer, demonstrating the Factory, Orchestrator, Repository, and Strategy patterns working together.

## 1. The Adapter Layer (Micro)

The `FilesystemAdapter` is responsible for pure I/O operations, encapsulating the raw interaction with the underlying file system.

```python
# src/filesystem/adapter.py
import os
from typing import Generator

class FilesystemAdapter:
    def write_bytes(self, path: str, data: bytes):
        """Writes raw bytes to a file."""
        with open(path, "wb") as f:
            f.write(data)

    def read_bytes_chunked(self, path: str, chunk_size: int = 4096) -> Generator[bytes, None, None]:
        """Reads bytes from a file in chunks."""
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def move(self, src: str, dst: str):
        """Atomically renames/moves a file."""
        os.replace(src, dst)

    def exists(self, path: str) -> bool:
        """Checks if a file or directory exists."""
        return os.path.exists(path)
```

## 2. The Persistence Layer (Meso)

This layer orchestrates serialization, integrity checks, and atomic writes using various strategies.

### Abstract Base Classes (Interfaces)

These are defined in `src/persistence/integrity/base.py` and `src/persistence/serialization/base.py` as shown in the main design document.

### Concrete Strategy Implementations

#### Integrity Strategies

```python
# src/persistence/integrity/sha256.py
import hashlib
from typing import Generator
from .base import IntegrityStrategy

class SHA256Strategy(IntegrityStrategy):
    def calculate(self, byte_generator: Generator[bytes, None, None]) -> str:
        hasher = hashlib.sha256()
        for chunk in byte_generator:
            hasher.update(chunk)
        return hasher.hexdigest()

    @property
    def algorithm_name(self) -> str:
        return "SHA-256"
```

#### Serialization Strategies

```python
# src/persistence/serialization/json_ser.py
import json
from typing import Any
from .base import SerializerStrategy

class JsonSerializer(SerializerStrategy):
    def serialize(self, data: Any) -> str:
        return json.dumps(data, indent=4)
    
    def deserialize(self, data_str: str) -> Any:
        return json.loads(data_str)

    @property
    def format_extension(self) -> str:
        return ".json"
```

### The Persistence Orchestrator (Meso Brain)

This class uses Composition to combine the different sub-services.

```python
# src/persistence/orchestrator.py
from typing import Any
from ..filesystem.adapter import FilesystemAdapter
from .integrity.base import IntegrityStrategy
from .serialization.base import SerializerStrategy

class PersistenceOrchestrator:
    def __init__(
        self, 
        adapter: FilesystemAdapter, 
        integrity: IntegrityStrategy, 
        serializer: SerializerStrategy
    ):
        self.adapter = adapter
        self.integrity = integrity
        self.serializer = serializer

    def save_atomic(self, path: str, data: Any) -> dict:
        # 1. Transform: Logic belonging to Serialization Strategy
        content_str = self.serializer.serialize(data)
        content_bytes = content_str.encode('utf-8')

        # 2. Audit: Logic belonging to Integrity Strategy
        def chunk_gen(): yield content_bytes
        checksum = self.integrity.calculate(chunk_gen())

        # 3. I/O: Logic belonging to the Adapter (Infrastructure)
        temp_path = f"{path}.tmp"
        self.adapter.write_bytes(temp_path, content_bytes)
        
        # Atomic swap via the Adapter/OS
        self.adapter.move(temp_path, path)

        return {"checksum": checksum, "size": len(content_bytes)}
```

### The Persistence Factory

The Factory acts as the "Assembly Line" for the Persistence Layer.

```python
# src/persistence/factory.py
import os
from typing import Dict, Type
from ..filesystem.adapter import FilesystemAdapter
from .orchestrator import PersistenceOrchestrator
from .integrity.base import IntegrityStrategy
from .integrity.sha256 import SHA256Strategy
from .integrity.md5 import MD5Strategy
from .serialization.base import SerializerStrategy
from .serialization.json_ser import JsonSerializer
from .serialization.csv_ser import CsvSerializer

class PersistenceFactory:
    def __init__(self, filesystem_adapter: FilesystemAdapter):
        self.adapter = filesystem_adapter
        
        self._serializer_map: Dict[str, SerializerStrategy] = {
            ".json": JsonSerializer(),
            ".csv": CsvSerializer(),
        }
        
        self._integrity_map: Dict[str, IntegrityStrategy] = {
            "high": SHA256Strategy(),
            "fast": MD5Strategy(),
        }

    def get_orchestrator(self, filename: str, security_level: str = "high") -> PersistenceOrchestrator:
        _, ext = os.path.splitext(filename.lower())
        serializer = self._serializer_map.get(ext)
        
        if not serializer:
            raise ValueError(f"No serialization strategy found for: {ext}")

        integrity = self._integrity_map.get(security_level)
        if not integrity:
            raise ValueError(f"Invalid security level specified: {security_level}")

        return PersistenceOrchestrator(
            adapter=self.adapter,
            integrity=integrity,
            serializer=serializer
        )
```

## 3. The User Access Layer (Macro)

The `ManifestRepository` interacts with the persistence factory to save its data.

```python
# src/manifest/repository.py
from ..persistence.factory import PersistenceFactory

class ManifestRepository:
    def __init__(self, persistence_factory: PersistenceFactory, root_path: str):
        self.factory = persistence_factory
        self.root_path = root_path

    def save(self, manifest_data: dict, manifest_name: str) -> dict:
        # The repository is responsible for defining the final path
        filename = f"{self.root_path}/{manifest_name}.json"
        
        # Get the correct tool for the job from the Factory
        orchestrator = self.factory.get_orchestrator(filename, security_level="high")
        
        # Use the tool to save the data
        return orchestrator.save_atomic(filename, manifest_data)
```

## 4. Wiring It All Together (Application Entry Point)

At the application's main entry point, you instantiate the infrastructure and inject it into the higher-level components.

```python
# main.py (simplified application entry point)

from src.filesystem.adapter import FilesystemAdapter
from src.persistence.factory import PersistenceFactory
from src.manifest.repository import ManifestRepository

def main():
    # --- Configuration ---
    DATA_DIR = "/srv/elite-dangerous-dev/pipeline/data"
    
    # 1. Initialize Infrastructure Layer (Micro)
    fs_adapter = FilesystemAdapter()

    # 2. Initialize Persistence Layer Factory (Meso)
    persistence_factory = PersistenceFactory(filesystem_adapter=fs_adapter)

    # 3. Initialize Service Layer Components (Macro), injecting dependencies
    manifest_repo = ManifestRepository(
        persistence_factory=persistence_factory, 
        root_path=f"{DATA_DIR}/manifests"
    )

    # --- Example Usage ---
    my_manifest_data = {
        "id": "edsm_systems_20260217", 
        "version": "1.0", 
        "files": ["systems_part1.json.gz", "systems_part2.json.gz"]
    }
    
    print("Attempting to save manifest...")
    result = manifest_repo.save(my_manifest_data, manifest_name="edsm_systems_manifest")
    print(f"Manifest saved successfully!")
    print(f"  -> Checksum (SHA-256): {result['checksum']}")
    print(f"  -> Size (bytes): {result['size']}")

if __name__ == "__main__":
    main()
```
