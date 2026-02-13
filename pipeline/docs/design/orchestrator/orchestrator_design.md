# ETL Pipeline: Component Orchestrator Design

In this Linux-based ETL architecture, the `PipelineOrchestrator` acts as the "Air Traffic Controller." It doesn't perform the heavy lifting (downloading, validating); instead, it coordinates the specialized classes that do.

This document details the design of a **component-specific orchestrator**. Its sole job is to manage the Extraction and initial Validation of data, living entirely within the `/etl/` component. This is a best practice that keeps code modular and testable, separating it from a potential future "Global Pipeline" orchestrator that might manage tasks across multiple components (e.g., ETL, Transformation, Loading).

## 1. Responsibilities

The orchestrator's primary responsibilities are to:
-   **Coordinate** the sequence of operations: Probe -> Download -> Validate -> Manifest.
-   **Make Decisions** based on configuration flags (`force_refresh`, `dry_run`) and pipeline state (ETags, checksums).
-   **Manage State** by interacting with the `ManifestManager` to check for existing records and register new ones.
-   **Handle Control Flow**, gracefully exiting or skipping steps when necessary.

## 2. Implementation

The class is initialized with its required "tools" (`SourceProber`, `DownloadContext`, `ValidatorClass`) and a `ManifestManager` instance for the `extractor` process.

```python
import logging
from typing import Optional, List
from common.config.settings import etl_settings
from extractor.source_probe.prober import SourceProber
from extractor.download.context import DownloadContext
from extractor.validation.validator import ValidatorClass
from common.manifests.manager import ManifestFactory, ManifestMetadata
from common.constants import ETLProcess

# Placeholder model imports for context
class ETLSource: pass
class DownloadEvent: pass
class ProbeResult: pass

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        # 1. Configuration & State Management
        self.config = etl_settings
        
        # Use the factory to get a manifest manager instance
        manifest_metadata = ManifestMetadata(
            process=ETLProcess.EXTRACTOR,
            etl_version="1.0.0",
            root_dir=self.config.manifest_path
        )
        self.manifest = ManifestFactory.get_manifest_manager(
            "downloads",
            path=self.config.manifest_path / "downloads.manifest.json",
            metadata=manifest_metadata
        )
        
        # 2. Tooling
        self.prober = SourceProber()
        self.download_context = DownloadContext()
        self.validator = ValidatorClass()

    def run_source(self, source: ETLSource) -> Optional[DownloadEvent]:
        """Main lifecycle for processing a single data source."""
        logger.info(f"--- Processing Source: {source.source_id} ---")

        # 1. PROBE: Get remote metadata without downloading the full file
        probe_result = self.prober.probe(source.connection)
        if not probe_result.success:
            logger.error(f"Probe failed for {source.source_id}: {probe_result.error_message}")
            return None

        # 2. DECIDE: Check if a download is necessary
        if self._is_download_needed(source, probe_result):
            
            # (Implicit Dry Run Check from config)
            if self.config.orchestration.dry_run:
                logger.info(f"[DRY RUN] Download needed for {source.source_id}, but skipping execution.")
                return None

            # 3. EXECUTE: Perform the download
            event = self.download_context.execute(source, probe_result)
            if not event:
                logger.error(f"Download execution failed for {source.source_id}.")
                return None

            # 4. VALIDATE: Check the downloaded artifact
            if self.validator.validate(event, source.expected_format):
                # 5. COMMIT: Record the successful event
                self.manifest.add_from_event(source, event)
                logger.info(f"Source {source.source_id} processed and updated successfully.")
                return event
            else:
                logger.error(f"Validation failed for {source.source_id}. File may be quarantined.")
                # Future logic: Move file to a quarantine directory
                return None
        
        logger.info(f"Source {source.source_id} is up to date. No action taken.")
        return None

    def _is_download_needed(self, source: ETLSource, probe: ProbeResult) -> bool:
        """The State-Check Logic Gate."""
        # Global override
        if self.config.orchestration.force_refresh:
            logger.info("`force_refresh` is True. Download is required.")
            return True

        last_record = self.manifest.get_record_by_source(source.source_id)
        
        if not last_record:
            logger.info("No previous record found in manifest. Download is required.")
            return True

        # Check for changes using remote metadata
        if probe.etag and last_record.etag != probe.etag:
            logger.info(f"ETag mismatch (Remote: {probe.etag} vs. Manifest: {last_record.etag}). Download is required.")
            return True
        
        # Final safety check: does the file actually exist where we expect it to?
        if not last_record.file_path.exists():
            logger.warning(f"Manifest record exists but file is missing at {last_record.file_path}. Download is required.")
            return True

        return False
```

## 3. Orchestration Logic and Data Flow

The `run_source` method follows a clear sequence of events and decisions, acting as a "transformer of state" by turning a source definition into a verified result in the manifest.

### 3.1. Visual Flowchart

This diagram illustrates the decision-making process within the `run_source` method.

```mermaid
graph TD
    A[Start: run_source(source)] --> B{1. Probe Source};
    B --> C{Probe Successful?};
    C -- No --> D[End: Log Probe Error];
    C -- Yes --> E{2. Download Needed?};
    E -- No --> F[End: Log "Source Up-to-Date"];
    E -- Yes --> G{3. Execute Download};
    G --> H{Download Succeeded?};
    H -- No --> I[End: Log Download Error];
    H -- Yes --> J{4. Validate File};
    J -- No --> K[End: Log Validation Error];
    J -- Yes --> L{5. Update Manifest};
    L --> M[End: Success];
```

### 3.2. Data Exchange Between Stages

The orchestrator manages the hand-off of data between each specialized component.

| Stage | Input Data | Data Exchange / Logic | Output Data |
| :--- | :--- | :--- | :--- |
| **Input** | `ETLSource` | The orchestrator reads the "Plan" of what data to get. | — |
| **Probing** | `ConnectionModel` | Passes URL/Headers to the `SourceProber`. | `ProbeResult` |
| **Extraction** | `ProbeResult` | Passes stream info and metadata to the `DownloadContext`. | `DownloadEvent` |
| **Validation** | `DownloadEvent` | Passes file path and checksum to the `Validator`. | `Boolean` (Pass/Fail) |
| **Output** | `DownloadEvent` | Writes a `ManifestRecord` to the manifest file. | `DownloadEvent` |


## 4. Key Decision Points (The "Gates")

The orchestrator's primary value comes from its decision-making gates, which prevent unnecessary or dangerous work.

1.  **The Freshness Gate (`_is_download_needed`)**: This is the main "cache check." It compares the metadata from the live probe (`ProbeResult`) against the historical record in the manifest (`ManifestRecord`). If ETags match and the local file exists, the entire download and validation process is skipped, saving server resources.
2.  **The Dry Run Gate (`orchestration.dry_run`)**: A global configuration flag that, if enabled, stops the orchestrator after a successful probe. This allows testing source availability and logic without using bandwidth.
3.  **The Validation Gate (`validator.validate`)**: The final quality check. It compares the physical file's content (via magic bytes and checksum) against the expected format. This is the gate that prevents corrupt data or HTML error pages from being recorded as "successful downloads" and passed to the next stage of the pipeline.

## 5. Design Rationale: The "ETL Component" Focus

By keeping this orchestrator specialized to the `etl` component, the architecture gains several advantages:

-   **Isolation:** The extraction logic can be developed and tested on a local machine (like your ProDesk) without needing a live database connection or other components to be online.
-   **Portability:** The entire `etl/` directory is self-contained. It can be moved to another Linux server, and as long as its `.env` file is present, the orchestrator will run correctly.
-   **Clarity:** This design avoids "God Object" syndrome, where one orchestrator becomes responsible for every line of code in the entire project, making it difficult to maintain and debug.
