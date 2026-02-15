# 4. Sampler Module: Data Management & Custody

This document outlines how the artifacts produced by the Sampler module are stored, managed, and linked, ensuring a clear and robust "Chain of Custody" from the original download to the final sample. This process is the explicit responsibility of the `ArtifactManager`.

## 4.1. The `ArtifactManager` & Its Artifacts

The `ArtifactManager` is responsible for the lifecycle of **derivative data**. It ensures that every sample file created in the `samples/` directory has a "birth certificate" (`sample.meta.json`) and a clear, cryptographic link to its parent download.

What it manages:
-   **The Sample File (`sample.json`):** The actual subset of data extracted from the source.
-   **The Sidecar Metadata (`sample.meta.json`):** The document that links the sample back to the source's `sha256` and records how it was made.
-   **Directory Integrity:** It ensures that the sample folder structure `etl/data/samples/[sha256]/` is created correctly.

## 4.2. Directory Structure: Raw vs. Samples

The pipeline enforces a strict separation between raw download files and the derivative sample artifacts. The directory structures are designed for different purposes.

### Download Structure (Timestamp-based)
Raw downloads are organized by date for chronological tracking.

```
etl/data/downloads/
└── YYYY/
    └── MM/
        ├── {source_id}_{dataset}_{process}_{timestamp}_v{version}.json.gz
        └── meta_{source_id}_{dataset}_{process}_{timestamp}_v{version}.json
```
- **Example File:** `spansh_systems_FULL_20260213_213251_v1-0.json.gz`
- **Example Meta:** `meta_spansh_systems_FULL_20260213_213251_v1-0.json`

The crucial `sha256` hash of the download is stored as a property *inside* this metadata file.

### Sample Structure (SHA256-based)
Sample artifacts are stored in a directory named after their **parent's SHA256 hash**. This creates an explicit, direct link for data lineage.

```
etl/data/samples/
└── [parent_sha256]/                # The SHA256 hash from the parent's metadata file
    ├── sample.json                 # The uncompressed sample file
    └── sample.meta.json            # The SampleMetadata artifact
```

## 4.3. The Hand-off: Main Pipeline to Orchestrator

The main ELT script remains clean. It relies on the `PathManager` to find pending downloads and correctly populate the `FileMetadata` object (including the `sha256` from the `meta_...json` file). This object is then handed to the `SamplerOrchestrator`.

```python
# --- Main Pipeline Script ---

# 1. Instantiate all independent services.
orchestrator = SamplerOrchestrator(...) # Composed with its dependencies
path_manager = PathManager()

# 2. The Main ELT Loop
for file_to_process in path_manager.get_pending_downloads():
    try:
        # 3. The Hand-off to the Orchestrator
        artifact_package = orchestrator.execute_sampling_flow(
            file_meta=file_to_process, # This object contains the parent sha256
            n_rows=500
        )
        print(f"Sample for parent {artifact_package.metadata.parent_sha256} created.")

    except Exception as e:
        logger.error(f"Failed to sample {file_to_process.file_path}: {e}")

```

### Summary of Custody

The **SHA256** hash acts as the primary key for data lineage.

1.  The `PathManager` finds a downloaded file (e.g., `..._v1-0.json.gz`) and reads its corresponding `meta_..._v1-0.json` file.
2.  It extracts the `sha256` property from the metadata and includes it in the `FileMetadata` object it prepares.
3.  The `SamplerOrchestrator` receives this `FileMetadata` object and passes the `parent_sha256` to the `ArtifactManager`.
4.  The `ArtifactManager` uses this `parent_sha256` to create the sample directory: `etl/data/samples/[parent_sha256]/`.
5.  It then generates a **new `sample_sha256`** for the `sample.json` it creates and saves both hashes in the final `sample.meta.json` file.

This process ensures a robust and traceable link between a time-stamped, named download and its content-addressed sample artifact.