# 2. Sampler Module: Architecture

The Sampler module is designed using a **Decoupled Orchestrator Pattern** with full **Dependency Injection**. This architecture intentionally separates concerns into distinct, instantiable components. A central `SamplerOrchestrator` acts as the "Brain," ensuring all other components work in the correct sequence. It provides a clean, single command to the main pipeline while delegating the heavy lifting to its injected dependencies.

## 2.1. The Orchestrator's Role & Core Components

The `SamplerOrchestrator` is responsible for the **Workflow**. It coordinates the other components, each of which has a clear, single responsibility and is provided to the orchestrator upon initialization.

| Component         | Role              | Orchestrator's Command to them                               |
| :---------------- | :---------------- | :----------------------------------------------------------- |
| **PathManager**   | The Source        | "Give me the file location and SHA256."                      |
| **Sniffer**       | The Scout         | "Look inside this file and tell me the structure."           |
| **SamplerFactory**| The Matchmaker    | "Based on the sniff, which Strategy should I use?"           |
| **Strategy**      | The Specialist    | "Extract exactly 100 rows from this compressed stream."      |
| **ArtifactManager**| The Archivist     | "Save these rows and create a linked metadata sidecar."      |

This pure dependency injection model maximizes testability and flexibility.

## 2.2. Implementation: The Decoupled Components

Here is how the key components are designed as standard classes, ready for injection.

### `sniffer.py` - The Sniffer Class
To enable injection, this is now a standard class with an `inspect` instance method.

```python
# src/sampler/sniffer.py
from .models import SnifferResult, FileStructure # Simplified

class Sniffer:
    """
    Performs deep inspection of a file's content to determine its structure.
    """
    def inspect(self, file_path: str, is_compressed: bool) -> SnifferResult:
        # In a real implementation, this would open the file,
        # read the first N bytes, check for magic numbers (e.g., gzip),
        # and peek at the first line to detect JSONL vs. JSON Array.
        # ...
        # Returning a dummy result for this example:
        return SnifferResult(structure=FileStructure.JSONL)
```

### `factory.py` - The Strategy Factory Class
The `@staticmethod` is removed, turning `get_strategy` into a regular instance method.

```python
# src/sampler/factory.py
from .strategies.base import SamplingStrategy
from .models import FileMetadata, SnifferResult, CompressionType

class SamplerFactory:
    """
    Maps metadata to a specific SamplingStrategy instance.
    """
    def get_strategy(self, metadata: FileMetadata, sniffer: SnifferResult) -> SamplingStrategy:
        if metadata.compression == CompressionType.GZIP:
            if sniffer.structure == FileStructure.JSONL:
                return GzipLineStrategy()
            return GzipIJsonStrategy()

        if sniffer.structure == FileStructure.CSV:
            return CsvStrategy()

        raise NotImplementedError(...)
```

### `orchestrator.py` - The `SamplerOrchestrator` (Revised)
The orchestrator now accepts all its dependencies in the constructor.

```python
# src/sampler/orchestrator.py
from .models import FileMetadata, SampleArtifact
from .factory import SamplerFactory
from .artifact import ArtifactManager
from .sniffer import Sniffer

class SamplerOrchestrator:
    """
    Coordinates the flow from raw file to documented sample using injected dependencies.
    """
    def __init__(
        self,
        sniffer: Sniffer,
        factory: SamplerFactory,
        artifact_manager: ArtifactManager
    ):
        self.sniffer = sniffer
        self.factory = factory
        self.artifact_mgr = artifact_manager

    def execute_sampling_flow(self, file_meta: FileMetadata, n_rows: int = 100) -> SampleArtifact:
        # 1. Inspect the content (Delegate to Sniffer instance)
        sniffer_record = self.sniffer.inspect(
            file_meta.file_path,
            is_compressed=(file_meta.compression != "none")
        )

        # 2. Select the tool (Delegate to Factory instance)
        strategy = self.factory.get_strategy(file_meta, sniffer_record)

        # 3. Perform extraction (Delegate to Strategy)
        raw_rows = strategy.get_sample(file_meta, n_rows)

        # 4. Finalize and Archive (Delegate to ArtifactManager instance)
        artifact = self.artifact_mgr.save_sample(
            data=raw_rows,
            parent_meta=file_meta,
            n_rows=n_rows,
            strategy_name=strategy.__class__.__name__
        )

        return artifact
```

## 2.3. Benefits of Pure Dependency Injection

-   **Superior Testability:** During unit testing of the `SamplerOrchestrator`, you can now pass in mock objects for the `Sniffer`, `Factory`, and `ArtifactManager` directly in the constructor. This provides complete control over the test environment without needing to patch modules.
-   **Explicit Contracts:** The `__init__` method of the orchestrator now serves as a clear, explicit declaration of its dependencies. There is no hidden reliance on static methods.