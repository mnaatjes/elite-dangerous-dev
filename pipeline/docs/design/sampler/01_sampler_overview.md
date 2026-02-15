# 1. Sampler Module: Overview

The Sampler module is a critical component of the ETL pipeline, designed to intelligently and efficiently extract a small, representative subset of data from massive source files.

## 1.1. The Goal

In the context of Elite Dangerous data, source files like the Spansh galaxy dumps or EDDN message logs can be gigabytes in size. Processing these entire files for development, schema validation, or quick analysis is impractical and resource-intensive.

The primary goals of the Sampler module are:
- **Efficiency:** Avoid reading the entirety of a large file just to understand its structure.
- **Intelligence:** Automatically detect the file's format and compression to apply the correct and most performant extraction strategy.
- **Traceability:** Create sample artifacts that are cryptographically and logically linked to their original source file, ensuring a clear "Chain of Custody."
- **Clarity & Testability:** Provide a clean, decoupled architecture where each component has a single responsibility, making the system easy to test, maintain, and extend.

## 1.2. High-Level Workflow

The sampler operates by coordinating several independent components under the direction of a central "Brain" or **`SamplerOrchestrator`**. This process transforms a raw downloaded file into a useful, metadata-rich sample artifact.

1.  **Input:** The process begins with the `PathManager`, which locates a raw data file (e.g., in `data/downloads/2026/03/`) and reads its corresponding `meta_...json` sidecar file. It packages all relevant information—including the file path, size, and the crucial **SHA256 hash** from the metadata—into a single `FileMetadata` object.

2.  **Orchestration (`SamplerOrchestrator`):** The `SamplerOrchestrator` receives the `FileMetadata` object and manages the workflow by delegating to specialized components:
    - It uses a **Sniffer** to perform a deep inspection of the file's contents.
    - It passes the file metadata and sniffer results to a **`SamplerFactory`**, which selects the appropriate `SamplingStrategy`.
    - The chosen `Strategy` is executed to read and extract a small number of records from the source file.
    - The extracted data and parent metadata are handed off to an **`ArtifactManager`**.

3.  **Output (`ArtifactManager`):** The `ArtifactManager` handles all I/O, creating the two final artifacts on the filesystem:
    - `sample.json`: A small, uncompressed file containing the sampled records.
    - `sample.meta.json`: A metadata file detailing *how* the sample was created and linking it back to its parent source file via its SHA256 hash.

This decoupled workflow, managed by the orchestrator, ensures that each part of the process is independent, testable, and robust.