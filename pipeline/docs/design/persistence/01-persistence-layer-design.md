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
│   └── adapters/
│       ├── abstract.py       # Defines the AbstractAdapter interface.
│       └── filesystem.py     # Wraps raw file I/O operations.
├── persistence/              # <-- MESO (PERSISTENCE) LAYER
│   ├── orchestrator.py       # [FACADE / ORCHESTRATOR] - Defines the persistence workflow.
│   ├── factories/            # [ABSTRACT FACTORY] - Assembles and configures orchestrators.
│   │   └── local.py
│   ├── resolvers/            # [STRATEGY RESOLVER] - Selects the correct strategies.
│   │   └── extension.py
│   ├── integrity/            # [STRATEGY] - Interchangeable hashing algorithms.
│   │   └── sha256.py
│   ├── serialization/        # [STRATEGY] - Interchangeable formatters.
│   │   └── json.py
│   └── interfaces/           # [INTERFACES / CONTRACTS] - Defines the ABCs for the layer.
│       ├── models.py         # Contains the PersistenceProfile DTO.
│       └── ...
└── manifest/                 # <-- MACRO (SERVICE) LAYER
    ├── repository.py         # [REPOSITORY] - Uses the Persistence Factory to save manifest objects.
    └── ...
```

### Data Flow

1.  A **Service** (e.g., `ManifestService`) decides to save a domain object.
2.  It uses its **Repository**, which calls the `PersistenceFactory` to get the correct persistence "tool" for the job (e.g., for `downloads/data.json`).
3.  The `PersistenceFactory` asks the `StrategyResolver` for the correct `PersistenceProfile` (containing the `Serializer` and `Integrity` strategies) based on the target string.
4.  The `PersistenceFactory` assembles and returns a pre-configured `PersistenceOrchestrator`, injecting the adapter and the resolved profile.
5.  The `Repository` tells the `PersistenceOrchestrator` to save the data.
6.  The `PersistenceOrchestrator` executes the save workflow:
    a.  Uses the `SerializerStrategy` from its profile to convert the data to a string or bytes.
    b.  Uses the `IntegrityStrategy` from its profile to calculate a checksum of the payload.
    c.  Passes the payload to the `FilesystemAdapter`.
7.  The `FilesystemAdapter` performs the atomic write operation.
8.  The checksum is returned up the chain to the `Repository`.

## 2. Core Patterns & Responsibilities

The persistence layer relies on several key design patterns to achieve its goals of modularity, safety, and testability.

### Persistence Orchestrator: The "Brain"

The `PersistenceOrchestrator` acts as a **Facade** and an **Orchestrator**. It simplifies the persistence process into a single `save()` call while coordinating the underlying strategies and adapters. Its responsibilities are:

-   **Workflow Coordination:** Executing the sequence: Serialize -> Hash -> Write.
-   **Abstraction:** Hiding all infrastructure details (like hashing and serialization) from the service layer.
-   **Integrity & Auditability:** Generating and returning checksums for all written data.

### Key Design Patterns

| Pattern | Role & Location | Why it's used |
| :--- | :--- | :--- |
| **Repository** | `manifest/repository.py` | To decouple the domain layer from persistence details. The repository "speaks" in terms of domain objects. |
| **Abstract Factory** | `persistence/factories/` | To assemble the correct `Orchestrator` with the right `Strategies`. This is the single entry point to the persistence package. |
| **Strategy Resolver** | `persistence/resolvers/` | To decouple the *selection* of strategies from the factory. It maps a target (like a file extension) to a specific `PersistenceProfile`. |
| **Strategy** | `persistence/integrity/`, `persistence/serialization/` | To make algorithms (hashing, serialization) interchangeable. This allows the system to support new formats and security levels without changing the core workflow. |
| **Adapter** | `filesystem/adapters/` | To wrap and isolate low-level OS calls. This makes the storage medium swappable (e.g., from local disk to S3) and improves testability. |
| **Template Method** | `persistence/orchestrator.py` | The `save` method acts as a template, defining the fixed steps of the persistence algorithm (serialize, calculate integrity, write). |

### Factory, Resolver, and Strategy: Complementary Roles

You need all three:
-   **Strategy Pattern (The "How"):** Provides the interchangeable parts (e.g., `JsonSerializer`, `SHA256Strategy`). It gives you variety.
-   **Resolver Pattern (The "Which"):** Provides the decision-making logic that selects the right strategies for a given task (e.g., a `.json` file gets a `JsonSerializer`).
-   **Factory Pattern (The "Who"/"When"):** Provides the "assembly line" that uses the `Resolver` to get the parts and builds the final `Orchestrator` tool.

Your service-level components should **only** interact with the Factory.

## 3. Implementation Details

### Strategy Interfaces (ABCs)

To ensure swappability, all strategies must adhere to a strict "contract" defined by an Abstract Base Class (ABC).

**Strategy Interfaces (from `persistence/interfaces/models.py`)**
```python
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
