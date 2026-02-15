# 1. Sampler Module: Overview

The Sampler module is a critical component of the ETL pipeline, designed to intelligently and efficiently extract a small, representative subset of data from massive source files.

## 1.1. The Goal

In the context of Elite Dangerous data, source files like the Spansh galaxy dumps or EDDN message logs can be gigabytes in size. Processing these entire files for development, schema validation, or quick analysis is impractical and resource-intensive.

The primary goals of the Sampler module are:
- **Efficiency:** Avoid reading the entirety of a large file just to understand its structure.
- **Intelligence:** Automatically detect the file's format (e.g., JSONL vs. a JSON array) and compression to apply the correct and most performant extraction strategy.
- **Traceability:** Create sample artifacts that are cryptographically and logically linked to their original source file, ensuring a clear "Chain of Custody."
- **Simplicity:** Provide a simple, "one-stop-shop" interface to the rest of the ETL pipeline.

## 1.2. High-Level Workflow

The sampler operates as a single, cohesive unit that transforms a raw downloaded file into a useful, metadata-rich sample artifact. This process follows a clear "Chain of Custody":

1.  **Input:** The process begins with a raw data file (e.g., `raw.json.gz`) and its associated filesystem metadata (path, size, etc.), which is provided by the `PathManager`.

2.  **Orchestration (`SamplerManager`):** A central `SamplerManager` orchestrates the entire process in one atomic operation.
    - It first uses an internal **Sniffer** to perform a deep inspection of the file's initial bytes to determine its true structure and format.
    - Based on the file's metadata and the sniffer's findings, an internal **Factory** selects the appropriate `SamplingStrategy` (e.g., a line-by-line reader for JSONL, or a streaming parser for a large JSON array).
    - The chosen strategy is executed to read and extract a small number of records from the source file.

3.  **Output:** The process generates two key artifacts:
    - `sample.json`: A small, uncompressed file containing the sampled records.
    - `sample.meta.json`: A metadata file detailing *how* the sample was created (which strategy was used, how many rows were taken) and linking it back to its parent source file via a cryptographic hash.

This entire workflow is encapsulated within the `SamplerManager`, ensuring that from the pipeline's perspective, sampling is a simple, reliable, and single command.