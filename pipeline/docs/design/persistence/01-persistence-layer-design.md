# Persistence Layer Design

This document provides a comprehensive overview of the persistence layer's architecture, design patterns, and implementation guidelines. It serves as the single source of truth for how data is safely and efficiently persisted within the pipeline.

## 1. Architectural Overview

The persistence layer acts as the "Meso-level" of the application, bridging the high-level "Macro" (Domain/Application) layer with the low-level "Micro" (Infrastructure) layer. Its primary responsibility is to ensure the safe, accurate, and verifiable movement of data from volatile memory (RAM) to permanent storage (Disk).

### Layered Architecture

The system is divided into three conceptual layers, which are mapped to distinct Python packages:

-   **Macro/Service Layer (`manifest`, `metadata`):** These are the "consumers" of persistence. They understand business objects (like `ManifestRecord`) and use the persistence layer as a black box via the **Repository Pattern**.
-   **Meso/Persistence Layer (`persistence`):** This is the "Service Provider." It coordinates the complex workflow of serialization, integrity checking, and atomic writing. It does not know about business objects, only about data structures like dictionaries.
-   **Micro/Adapter Layer (`filesystem`):** This is the "Low-Level Component." It is the only layer that interacts directly with the operating system's file system. It knows nothing about data formats or business rules, only bytes and paths.

### Package Structure & Component Interaction

The interaction between these layers follows a strict, decoupled flow, enforced by the package structure:

```
pipeline/src/
├── filesystem/               <-- MICRO (ADAPTER) LAYER
│   ├── adapter.py            # Wraps raw file I/O operations.
│   └── ...
├── persistence/              # <-- MESO (PERSISTENCE) LAYER
│   ├── factory.py            # [ABSTRACT FACTORY] - The main entry point for this package.
│   ├── orchestrator.py       # [FACADE / ORCHESTRATOR] - Defines the persistence workflow.
│   ├── integrity/            # [STRATEGY] - Interchangeable hashing algorithms (e.g., SHA256).
│   └── serialization/        # [STRATEGY] - Interchangeable formatters (e.g., JSON, CSV).
└── manifest/                 # <-- MACRO (SERVICE) LAYER
    ├── repository.py         # [REPOSITORY] - Uses the Persistence Factory to save manifest objects.
    └── ...
```

### Data Flow

1.  A **Service** (e.g., `ManifestService`) decides to save a domain object.
2.  It uses its **Repository**, which calls the `PersistenceFactory` to get the correct persistence "tool" for the job.
3.  The `PersistenceFactory` assembles and returns a pre-configured `PersistenceOrchestrator`.
4.  The `Repository` tells the `PersistenceOrchestrator` to save the data.
5.  The `PersistenceOrchestrator` executes the save workflow:
    a.  Uses a `SerializerStrategy` to convert the data to a string.
    b.  Encodes the string to bytes (`utf-8`).
    c.  Uses an `IntegrityStrategy` to calculate a checksum of the bytes.
    d.  Passes the bytes to the `FilesystemAdapter`.
6.  The `FilesystemAdapter` performs the atomic write operation (write to `.tmp` file, then `os.replace`).
7.  The checksum and file size are returned up the chain to the `Repository`, which may store this metadata.

## 2. Core Patterns & Responsibilities

The persistence layer relies on several key design patterns to achieve its goals of modularity, safety, and testability.

### Persistence Orchestrator: The "Brain"

The `PersistenceOrchestrator` acts as a **Facade** and an **Orchestrator**. It simplifies the persistence process into a single `save_atomic()` call while coordinating the underlying strategies and adapters. Its responsibilities are:

-   **Workflow Coordination:** Executing the sequence: Serialize -> Encode -> Hash -> Write -> Rename.
-   **Data Transformation:** Delegating object-to-byte conversion to the appropriate strategies.
-   **Integrity & Auditability:** Generating and returning checksums for all written data.
-   **Safety & Atomicity:** Ensuring that file writes are transactional and that no corrupted "half-files" are left behind.
-   **Abstraction:** Hiding all infrastructure details from the service layer.

### Key Design Patterns

| Pattern | Role & Location | Why it's used |
| :--- | :--- | :--- |
| **Repository** | `manifest/repository.py` | To decouple the domain layer from persistence details. The repository "speaks" in terms of domain objects. |
| **Abstract Factory** | `persistence/factory.py` | To select and assemble the correct `Orchestrator` with the right `Strategies`. This is the single entry point to the persistence package. |
| **Strategy** | `persistence/integrity/`, `persistence/serialization/` | To make algorithms (hashing, serialization) interchangeable. This allows the system to support new formats and security levels without changing the core workflow. |
| **Adapter** | `filesystem/adapter.py` | To wrap and isolate low-level OS calls. This makes the storage medium swappable (e.g., from local disk to S3) and improves testability. |
| **Template Method** | `persistence/orchestrator.py` | The `save_atomic` method acts as a template, defining the fixed steps of the persistence algorithm. |

### Factory vs. Strategy: Complementary Roles

You need both:
-   **Strategy Pattern (The "How"):** Provides the interchangeable parts (e.g., `JsonSerializer`, `SHA256Strategy`). It gives you variety.
-   **Factory Pattern (The "Who"/"When"):** Provides the "assembly line" that selects the right strategies for a given task (e.g., a `.json` file) and builds the final `Orchestrator` tool. It gives you selection and simplicity.

Your service-level components should **only** interact with the Factory.

## 3. Implementation Details

### Strategy Interfaces (ABCs)

To ensure swappability, all strategies must adhere to a strict "contract" defined by an Abstract Base Class (ABC).

**Integrity Strategy Interface:**
```python
from abc import ABC, abstractmethod
from typing import Generator

class IntegrityStrategy(ABC):
    @abstractmethod
    def calculate(self, byte_generator: Generator[bytes, None, None]) -> str:
        """Consumes a stream of bytes and returns a hex digest."""
        pass

    @property @abstractmethod
    def algorithm_name(self) -> str:
        """Returns the name of the algorithm (e.g., 'SHA-256')."""
        pass
```

**Serializer Strategy Interface:**
```python
from abc import ABC, abstractmethod
from typing import Any

class SerializerStrategy(ABC):
    @abstractmethod
    def serialize(self, data: Any) -> str:
        """Converts Python objects/dicts into a formatted string."""
        pass

    @abstractmethod
    def deserialize(self, data_str: str) -> Any:
        """Converts a formatted string back into Python objects/dicts."""
        pass

    @property @abstractmethod
    def format_extension(self) -> str:
        """Returns the preferred file extension (e.g., '.json')."""
        pass
```

### Concrete Strategies

The system can support any number of concrete implementations for these interfaces.

-   **Integrity:** `SHA256Strategy`, `MD5Strategy`, `ByteCounterStrategy`.
-   **Serialization:** `JsonSerializer`, `CsvSerializer`, `YamlSerializer`.

## 4. Best Practices

-   **Dependency Injection:** The `FilesystemAdapter` and `PersistenceFactory` should be instantiated once at application startup and injected into the services that need them. Avoid Singletons.
-   **Stateless Services:** Keep the `PersistenceOrchestrator` stateless. All necessary data should be passed into its methods, not stored on the instance.
-   **Explicit Encoding:** Always specify `utf-8` when encoding and decoding strings to prevent cross-platform issues.
-   **Use Context Managers:** The `FilesystemAdapter` must use `with open(...)` to ensure file handles are always closed, preventing resource leaks.
-   **The "Dumb" Adapter:** The adapter should have zero business or data-formatting logic. It only deals with bytes and paths.

---

For a complete, end-to-end code example demonstrating how these patterns are wired together, see [02-implementation-example.md](./02-implementation-example.md).
