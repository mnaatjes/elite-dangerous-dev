# 2. Sampler Module: Architecture

The Sampler module is designed using a consolidated **Orchestrator Pattern** (also known as a Facade). A single `SamplerManager` class provides a simple, unified interface for the entire sampling process, encapsulating the complexity of file inspection, strategy selection, and execution.

## 2.1. The `SamplerManager` Orchestrator

The `SamplerManager` is the "one-stop shop" for the pipeline. It is initialized from a file's basic metadata and, in one command, handles the entire workflow of producing a sample. This design was chosen to:
- **Simplify the public API:** The rest of the pipeline doesn't need to know about sniffers or factories; it just calls `SamplerManager.from_file(meta).run()`.
- **Ensure Atomic Operations:** The process of sniffing, selecting a strategy, and sampling is tied together, preventing steps from being run out of order.
- **Promote Context Awareness:** The manager holds all metadata, sniffer results, and strategy information, making it easy to generate rich logs and final metadata artifacts.

## 2.2. Core Components & Single-Responsibility Principle

While the `SamplerManager` is a consolidated class, its internal components and methods are designed to adhere to the Single-Responsibility Principle (SRP).

-   **`SamplerManager` (The Orchestrator)**
    -   **Responsibility:** To manage the end-to-end sampling process for a single file. It orchestrates the other components to produce a sample artifact.

-   **`Sniffer` (The Inspector)**
    -   **Responsibility:** To perform deep inspection of a file's content to determine its structure (e.g., `JSONL` vs. `JSON_ARRAY`), encoding, and compression.
    -   It is a distinct utility class that is *used by* the `SamplerManager` during its initialization. Its logic is not mixed into the manager's.

-   **`_select_strategy()` (The Internal Factory)**
    -   **Responsibility:** To select the correct `SamplingStrategy` based on the file's metadata and the `Sniffer`'s findings.
    -   This private method acts as the "Factory." Its logic is solely focused on decision-making, cleanly separating the "what" from the "how."

-   **`SamplingStrategy` (The Worker)**
    -   **Responsibility:** To extract sample data from a specific type of file.
    -   Each strategy class (e.g., `GzipLineStrategy`, `GzipIJsonStrategy`) has one job: read a specific format and yield records. These classes are completely decoupled from the `SamplerManager` and from each other.

## 2.3. Detailed Pipeline Flow & Implementation

The following code demonstrates the consolidated `SamplerManager` and the flow of operations.

```python
# Assumes other modules (models, strategies, sniffer) are in place.
from .models import FileMetadata, SnifferResult, SampleOutput
from .strategies.base import SamplingStrategy
from .sniffer import Sniffer

class SamplerManager:
    """
    Acts as a consolidated orchestrator (Facade) for the entire sampling process.
    """
    def __init__(self, metadata: FileMetadata, sniffer_record: SnifferResult):
        self.metadata = metadata
        self.sniffer = sniffer_record
        # The Manager finds the strategy immediately upon creation.
        self._strategy: SamplingStrategy = self._select_strategy()

    @classmethod
    def from_file(cls, path_manager_data: FileMetadata) -> 'SamplerManager':
        """
        The primary 'Factory' entry point. It orchestrates the sniffer
        and initializes the Manager in one command.
        """
        # 1. Perform deep inspection
        sniffer_record = Sniffer.inspect(
            path_manager_data.file_path,
            is_compressed=(path_manager_data.compression != "none")
        )
        # 2. Return an initialized manager instance
        return cls(path_manager_data, sniffer_record)

    def _select_strategy(self) -> SamplingStrategy:
        """
        Internal Factory logic: The Decision Matrix.
        This method's single responsibility is to choose the right strategy.
        """
        if self.metadata.compression == "gzip":
            if self.sniffer.structure == FileStructure.JSONL:
                return GzipLineStrategy()
            return GzipIJsonStrategy()

        if self.sniffer.structure == FileStructure.CSV:
            return CsvStrategy()

        raise NotImplementedError("No strategy found for the given file type.")

    def run(self, n_rows: int = 100) -> SampleOutput:
        """
        The main orchestration method. Executes sampling and creates the artifact.
        """
        # 3. The chosen strategy does the work of extracting data
        raw_data = self._strategy.get_sample(self.metadata, n_rows)

        # 4. The manager handles the final artifact creation (custody logic)
        return self._create_sample_artifact(raw_data)

    def _create_sample_artifact(self, data: list) -> SampleOutput:
        """Creates the final sample file and its metadata."""
        # Logic to write to etl/data/samples/[sha256]/...
        # Logic to generate and write sample.meta.json
        # Returns a SampleOutput object with paths and metadata
        pass
```

### Disadvantages to Watch For

The primary risk of this pattern is creating a "God Object." The `SamplerManager`'s scope must be kept **strictly focused on sampling**. If logic for downloading, uploading, or transforming data is added, it will violate SRP and become difficult to maintain.