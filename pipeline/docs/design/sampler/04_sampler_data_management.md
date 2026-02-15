# 4. Sampler Module: Data Management & Custody

This document outlines how the artifacts produced by the Sampler module are stored, managed, and linked, ensuring a clear and robust "Chain of Custody" from the original download to the final sample. This process is the explicit responsibility of the `ArtifactManager`.

## 4.1. The `ArtifactManager` & Its Artifacts

The `ArtifactManager` is responsible for the lifecycle of **derivative data**. In an ELT project, you never want "orphaned" files. If a file exists in your `samples/` directory, the `ArtifactManager` ensures it has a "birth certificate" (`sample.meta.json`) and a clear link to its parent.

What it manages:
-   **The Sample File (`sample.json`):** The actual subset of data extracted from the source.
-   **The Sidecar Metadata (`sample.meta.json`):** The document that links the sample back to the source `sha256` and records the "regime" (e.g., were these the first 100 rows or a random 10%?).
-   **Directory Integrity:** It ensures that the folder structure `etl/data/samples/[sha256]/` is created correctly on the Linux filesystem.

## 4.2. Directory Structure: Raw vs. Samples

The `ArtifactManager` enforces a strict separation between immutable raw source files and ephemeral, derivative sample files.

```
etl/data/
├── downloads/
│   └── [sha256]/                   # Unique ID (hash of the raw file)
│       ├── raw.json.gz             # The immutable, original source file
│       └── download.meta.json      # Metadata from the downloader (ETag, URL, etc.)
├── samples/
│   └── [sha256]/                   # Replicated ID, managed by ArtifactManager
│       ├── sample.json             # The uncompressed sample file
│       └── sample.meta.json        # The SampleMetadata artifact
└── ...
```

## 4.3. The Hand-off: Main Pipeline to Orchestrator

The main ELT script is responsible for composing the final application from its independent components. It instantiates the service classes and injects them into the orchestrator, which then handles the workflow.

```python
# --- Main Pipeline Script ---
from .sampler import SamplerOrchestrator, Sniffer, SamplerFactory, ArtifactManager

# 1. Instantiate all independent services.
#    This is the composition root of the application.
sniffer_svc = Sniffer()
factory_svc = SamplerFactory()
artifact_svc = ArtifactManager(base_dir=Path("etl/data/samples"))
path_manager = PathManager() # Assuming a PathManager service

# 2. Compose the main orchestrator by injecting its dependencies.
orchestrator = SamplerOrchestrator(
    sniffer=sniffer_svc,
    factory=factory_svc,
    artifact_manager=artifact_svc
)

# 3. The Main ELT Loop
for file_to_process in path_manager.get_pending_downloads():
    try:
        # 4. The Hand-off to the Orchestrator
        # The orchestrator now has everything it needs to run the entire flow.
        artifact_package = orchestrator.execute_sampling_flow(
            file_meta=file_to_process,
            n_rows=500
        )
        print(f"Sample created at: {artifact_package.sample_path}")
        print(f"Linked to source: {artifact_package.metadata.parent_sha256}")

    except NotImplementedError as e:
        logger.error(f"Failed to sample {file_to_process.file_path}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during sampling: {e}")

```

### Summary of Custody

The **SHA256** hash acts as the primary key across the entire pipeline. The `SamplerOrchestrator` ensures this `parent_sha256` is passed to the `ArtifactManager`, which then embeds it into the final `SampleArtifact`, guaranteeing an unbroken and traceable data lineage.