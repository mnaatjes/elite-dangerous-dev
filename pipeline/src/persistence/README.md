# 🛠 Persistence Module Documentation

The module is designed to be shape-aware. You don't tell it how to save; you just give it data, and it resolves the best strategy based on the data's structure and your requirements.

## 1. PersistenceManager (The Constructor)

The `PersistenceManager` is the top-level assembly point. It bootstraps the `StrategyLibrary`, registers all your serializers and integrity checkers, and provides a "Universal Orchestrator."

*   **Usage:** Instantiate this once at the start of your application.
*   **Location:** `src/persistence/manager.py`

```python
from src.adapters.filesystem import LocalFilesystemAdapter
from src.persistence import PersistenceManager

# Setup infrastructure
adapter = LocalFilesystemAdapter(base_path="/srv/data")
manager = PersistenceManager(adapter)

# Get the mission control object
orchestrator = manager.get_orchestrator()
```

## 2. PersistenceOrchestrator (Mission Control)

The Orchestrator is the only component your application code interacts with. It uses **Intent-Based Resolution** to decide between Atomic (whole-file) and Streaming (line-by-line) operations.

### `save(target, data, policy=None)`
*   **Atomic Path:** Triggered when data is a `dict`, `list`, `str`, or `bytes`.
*   **Streaming Path:** Triggered when data is a `Generator` or `Iterator`.
*   **Returns:** The integrity checksum (e.g., a SHA256 hex string or empty string).

```python
# Atomic Example (Settings, small profiles)
orchestrator.save("configs/user.json", {"theme": "dark"})

# Streaming Example (Elite Dangerous Star Maps)
def star_gen():
    yield {"name": "Sol"}
    yield {"name": "Maia"}

orchestrator.save("exports/stars.ndjson", star_gen(), policy="sha256_stream")
```

## 3. StrategyLibrary (The Resolver)

The Library acts as a "Dating App" for data and strategies. It matches a Category (`SERIALIZER`/`INTEGRITY`) and a Capability (`ATOMIC`/`STREAM`) to the best possible tool in the registry.

### Resolution Logic:
1.  **Name Match:** If you pass a policy, it looks for that specific name first.
2.  **Specialized Match:** If no name is provided, it looks for a non-default strategy that matches the capability (e.g., finding `sha256_stream` for a stream).
3.  **Default Fallback:** Finally, it falls back to the registered default (e.g., `json` or `no_op`).

## 4. Serializers (The Formatters)

These define how Python objects are turned into strings or bytes for storage.

| Component | Type | Format | Output |
| :--- | :--- | :--- | :--- |
| `JSONSerializer` | Atomic | Standard JSON | `str` |
| `NDJsonSerializer` | Streaming | Line-delimited JSON | `str` (with 
) |
| `BinarySerializer` | Atomic | Raw Bytes | `bytes` |

## 5. Integrity Strategies (The Fingerprints)

These ensure that your star-data hasn't been corrupted.

*   **NoOpIntegrity:** The default "pass-through." Returns an empty string. Good for non-critical logs.
*   **StreamingSha256Strategy:** Calculates a rolling hash. It consumes bytes chunk-by-chunk, meaning it can hash a 10GB file without using more than a few kilobytes of RAM.

---

## 🏗️ How to Add a Strategy

Every strategy, whether it formats data (Serializer) or validates it (Integrity), follows a three-step lifecycle:
1.  **Inherit:** Pick the correct Abstract Base Class (ABC).
2.  **Implement:** Fill out the required methods (the "Interface Contract").
3.  **Register:** Add it to the `PersistenceManager` bootstrap.

### 1. Adding an Atomic Strategy
**Use case:** When you want to process a file as a single, complete unit (e.g., XML, TOML, or a specialized Binary blob).

```python
# src/persistence/strategies/serialization/atomic/xml.py
from typing import Any
from ..abstracts import AtomicSerializer
from ...const import Capability, Category

class AtomicXmlSerializer(AtomicSerializer):
    NAME = "xml"
    CATEGORY = Category.SERIALIZER
    CAPABILITIES = Capability.ATOMIC  # This tells the library it's for whole files
    
    def encode(self, data: Any) -> str:
        # Implementation logic to turn dict -> XML string
        return f"<root>{data}</root>"

    def decode(self, payload: str) -> Any:
        # Implementation logic to turn XML string -> dict
        return {"data": payload}
```

### 2. Adding a Stateful (Streaming) Strategy
**Use case:** When you need to handle data chunk-by-chunk (e.g., massive Elite Dangerous star maps or rolling logs).

```python
# src/persistence/strategies/serialization/stateful/csv.py
import csv
import io
from typing import Any, Iterable
from ..abstracts import StreamingSerializer

class CsvStreamingSerializer(StreamingSerializer):
    NAME = "csv"
    CAPABILITIES = Capability.STREAM

    def encode_item(self, item: dict) -> str:
        """Encodes a single row. Note: This simple version ignores headers."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(item.values())
        return output.getvalue()

    def finalize(self) -> str:
        """CSVs don't usually need a footer."""
        return ""
        
    def decode_stream(self, stream: Iterable[str]) -> Iterable[dict]:
        """Reads line by line."""
        reader = csv.DictReader(stream)
        for row in reader:
            yield row
```

### 3. The Registration Logic
Once you've written your class, you must "hand it to the library" inside your manager.

```python
# src/persistence/manager.py

def _bootstrap_library(self) -> StrategyLibrary:
    lib = StrategyLibrary()
    
    # Registering your new tools
    lib.register(AtomicXmlSerializer)
    lib.register(CsvStreamingSerializer)
    
    return lib
```

---

## 🚦 Strategy Decision Matrix

| Feature | Atomic Strategy | Stateful (Streaming) Strategy |
| :--- | :--- | :--- |
| **Inherits From** | `AtomicSerializer` / `AtomicIntegrity` | `StreamingSerializer` / `StreamingIntegrity` |
| **Memory Goal** | Ease of use (loads all at once) | Safety (never loads full file) |
| **Best For** | Configs, Settings, User Profiles | Journals, Star Maps, Large ETL exports |
| **Key Methods** | `encode()`, `decode()`, `calculate()` | `encode_item()`, `decode_stream()`, `update()` |
| **Data Shape** | `dict`, `list`, `bytes` | `Generator`, `Iterator`, `File Handle` |

> **💡 Pro-Tip:** When adding Stateful strategies, always ensure your `encode_item` or `update` methods handle strings and bytes consistently. If a binary streaming strategy is used, ensure `CAPABILITIES` are correctly flagged so the Orchestrator knows to use `"wb"`.

---

## 🔍 The Decision Engine: `find()`

The `find()` method is the heart of your `StrategyLibrary`. It resolves the correct tool based on: **Category**, **Name (Policy)**, and **Capabilities**.

### Method Signature
```python
def find(
    self, 
    category: Category, 
    name: Optional[str] = None, 
    required_capabilities: Optional[Capability] = None
) -> Optional['StrategyManifest']:
```

### Resolution Hierarchy (The "Waterfall")
1.  **Explicit Name (High Priority):** Looks for an exact name match (e.g., "sha256_stream").
2.  **Default with Capability (Smart Default):** Checks the default strategy for that category.
3.  **Specialized Capability Match (Fallback):** Scans all registered strategies for a capability match if the default fails.
4.  **None:** Returns `None` if no match is found.

---

## 🏛️ The Repository Pattern

The Repository acts as the "Maître d'" of your data layer. It provides a clean, domain-specific API and decouples business logic from raw I/O.

### Basic Structure
```python
# src/repositories/star_system_repository.py
from typing import Iterable, Any
from src.persistence.orchestrator import PersistenceOrchestrator

class StarSystemRepository:
    def __init__(self, orchestrator: PersistenceOrchestrator):
        self._orchestrator = orchestrator
        self._base_path = "data/systems"

    def save_profile(self, system_name: str, data: dict):
        """Atomic save for a single system summary."""
        path = f"{self._base_path}/{system_name.lower()}.json"
        return self._orchestrator.save(path, data)

    def export_bulk(self, systems: Iterable[dict], filename: str):
        """Streaming save for massive datasets."""
        path = f"exports/{filename}.ndjson"
        return self._orchestrator.save(path, systems, policy="sha256_stream")
```

### Why this matters for your ETL
*   **Grep-ability:** File-naming logic is centralized.
*   **Decoupling:** Changes to the persistence layer don't break business logic.
*   **Testing:** Easy to inject a mock orchestrator for unit tests.

---

## 🛠 Summary Checklist
- [ ] **Implement `read()`:** To pull Atomic data back into a `dict`.
- [ ] **Implement `read_stream()`:** To pull Streaming data back into a generator.
- [ ] **Compression Decorator:** Adding `.gz` support to existing serializers.
