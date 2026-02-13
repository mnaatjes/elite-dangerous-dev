# ETL Pipeline Design - Phase 2: HTTP Layer and Data Integrity

This document outlines the design and architectural considerations for the next phase of the ETL Pipeline, focusing on the HTTP layer for data acquisition and ensuring data integrity. The approach shifts from simple data handling to robust management of server conversations, incorporating advanced patterns and tools.

## 1. The "Strategy Pattern" Explained

The Strategy Pattern is a design approach that allows for interchangeable algorithms (strategies) to be selected at runtime. Instead of using a single, complex function with numerous conditional statements to handle different data types or download regimes, we create small, specialized "strategy" objects. Each strategy implements a common interface (method), allowing the main application logic to remain clean and decoupled from the specific implementation details of how a file is processed or downloaded.

For example, instead of a monolithic download function that grows with every new file type, we can have distinct `JsonStrategy`, `GzipStrategy`, and `BinaryStrategy` classes. Each of these strategies encapsulates the specific logic for its respective data type. The main code simply selects the appropriate strategy and calls its generic `execute()` method, without needing to know the internal complexities of how each type is handled. This makes the system more modular, easier to maintain, and extensible to new data types.

## 2. Updated Goals & Requirements Matrix

This matrix details the refined goals and implementation logic for key aspects of the ETL pipeline.

| Category          | Requirements                 | Implementation Logic                                                                                                                                              |
| :---------------- | :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Identity**      | Rolling SHA-256 Hash         | Generate the hash incrementally during the stream download. This hash will serve as the primary key for the manifest record, ensuring unique identification. |
| **Validation**    | Multivariate Integrity       | Implement a tiered defense using ETag (server-side), Content-MD5 (if provided), and local SHA-256 to ensure robust data integrity.                          |
| **Download Regime** | Regime Selection             | Employ the Strategy Pattern to dynamically swap between Json, GzippedJson, or Binary download logic based on initial HEAD request results.                 |
| **Audit (Record)** | File-Level Metadata          | Store critical server headers (e.g., `Last-Modified`) and file-system statistics within the `ManifestRecord` for comprehensive auditing.                      |
| **Probing**       | Sampling & Magic             | Utilize HTTP Range requests to inspect the first 1KB of a file, confirming the download "Regime" before initiating the full download.                       |

## 3. What is `httpx`?

`httpx` is a modern, fully featured HTTP client for Python, serving as the successor to the popular `requests` library. It offers significant advantages for this pipeline:

-   **HTTP/2 Support:** `httpx` inherently supports HTTP/2, which is utilized by services like Spansh, leading to more efficient communication.
-   **Asynchronous Requests:** It allows for asynchronous operations, which is crucial for building responsive and efficient data pipelines that can handle multiple tasks concurrently.
-   **Streaming Capabilities:** `httpx` excels at streaming large files. This feature is fundamental for generating the Rolling SHA-256 hash without loading entire multi-gigabyte files into RAM, thereby optimizing memory usage.

## 4. Architectural Solutions & Patterns

### A. The "Rolling Hash" Pattern (Identity)

Generating the SHA-256 hash incrementally during the file download is a best practice for handling large data streams. This pattern ensures that the data's integrity can be verified and used as a unique identifier without consuming excessive memory.

The process involves:
1.  Initializing a `hashlib.sha256()` object before the download begins.
2.  Within the download loop, after reading each `chunk` of data (e.g., `chunk = response.read()`), updating the hash object: `sha256_obj.update(chunk)`.
3.  Simultaneously, writing the `chunk` to disk.
4.  Once the entire file has been downloaded, the final hash can be retrieved using `sha256_obj.hexdigest()`, which then serves as the file's unique ID.

### B. The Integrity Tier (Validation)

To ensure robust data validation, a tiered integrity approach is proposed, leveraging various metadata available during the download process. This pattern can be implemented using a "Metadata Collector" approach.

-   **Tier 1 (Server-Side):** Capture and store server-provided headers such as `ETag` and `Last-Modified`. These provide external indicators of file versioning and modification.
-   **Tier 2 (Transport-Level):** Capture `Content-Length` from the HTTP headers to verify that the entire file stream was received without truncation.
-   **Tier 3 (Local-Level):** Utilize the locally generated SHA-256 hash for absolute content integrity verification.

All three tiers of validation metadata should be stored within the `ManifestRecord`. On subsequent pipeline runs, if the `ETag` from the server matches the stored `ETag`, the download can be skipped entirely, optimizing bandwidth and processing time.

## 5. Record Metadata vs. Manifest Metadata (Audit)

It's crucial to differentiate between `ManifestMetadata`, which pertains to the overall manifest file (the "Box"), and the detailed `Record Metadata` that applies to individual downloaded files (the "Items"). The `Record Metadata` (to be stored in a `meta.json` file or directly within the `ManifestRecord` for each item) should include:

-   `source_url`: The original URL from which the file was downloaded.
-   `etag`: The `ETag` header value from the server.
-   `last_modified_server`: The `Last-Modified` header value from the server, indicating the last time the resource was modified on the server.
-   `download_timestamp`: The local timestamp when the file was successfully downloaded.
-   `content_type`: The `Content-Type` header (e.g., `application/gzip`, `application/json`).
-   `content_length`: Both the expected `Content-Length` from the header and the actual size of the downloaded file.
-   `sha256`: The locally generated SHA-256 hash of the downloaded file.

## 6. Proposed Class Structure

To implement the above architectural solutions, the following core classes are proposed:

### `SourceProber` (The Inspector)
-   **Purpose:** To perform initial inspections of a remote source to determine its characteristics before a full download.
-   **Method:** `probe_source(url)`
-   **Action:** Executes an HTTP HEAD request and a partial GET request (using `Range` header for the first 1KB of data).
-   **Returns:** A `RemoteFileIntent` object, encapsulating critical information such as file size, ETag, and an inferred "Magic" type (e.g., content type detection from the initial bytes).

### `DownloadContext` (The Orchestrator)
-   **Purpose:** To orchestrate the download process, selecting and utilizing the appropriate download strategy.
-   **Functionality:**
    -   Takes the `RemoteFileIntent` object returned by the `SourceProber`.
    -   Based on the information within `RemoteFileIntent`, it selects the correct `DownloadStrategy` (e.g., `GzipDownloadStrategy`, `JsonDownloadStrategy`).
    -   Manages the `httpx.Client` session, ensuring efficient and persistent connections.

### `DownloadStrategy` (The Base Class/Interface)
-   **Purpose:** Defines the interface for all specific download strategies and provides common functionalities. This will likely be an abstract base class.
-   **Subclasses:**
    -   `GzipDownloadStrategy`: Implements logic specific to downloading and decompressing gzipped content, including handling the rolling hash during decompression.
    -   `JsonDownloadStrategy`: Implements logic for streaming and parsing JSON content, and managing the rolling hash for JSON data.
    -   Other specialized strategies as needed (e.g., `BinaryDownloadStrategy`).
-   **Method:** `execute(url, path)`
    -   Handles the core download logic, including managing the `httpx` stream, generating the rolling hash during the stream, and writing chunks to the specified `path`.
    -   Ensures that metadata for auditing and validation is collected during the execution.