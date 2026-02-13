# Module: Downloader System

**Source Files:**
-   `src/extractor/download/context.py`
-   `src/extractor/download/base.py`
-   `src/extractor/download/regimes/gzip.py`
-   `src/extractor/download/event.py`

The downloader system is responsible for efficiently and safely downloading files from remote sources. It is designed around the **Strategy Pattern**, allowing different download methods (or "regimes") to be used for different file types, while the main entry point remains consistent.

## 1. Architecture

The system is composed of a context class, an abstract base class for strategies, concrete strategy implementations, and a result model.

-   **`DownloadContext`:** The primary entry point for the download process. It is responsible for selecting the correct download strategy, managing file paths, and returning a final `DownloadEvent`.
-   **`DownloadStrategy` (ABC):** An Abstract Base Class that defines the contract for all download regimes. It ensures that every strategy has a `download()` method with a consistent signature.
-   **`GzipRegime`:** A concrete implementation of `DownloadStrategy` specifically for downloading gzip-compressed files. It handles streaming the content, calculating the SHA-256 checksum on the fly, and writing the file to disk.
-   **`DownloadEvent`:** An immutable Pydantic model that acts as a "receipt" for a completed download, containing the file path, size, checksum, and timestamps.

### How it Works

1.  The `DownloadContext` is initialized with a `PathManager`.
2.  Its `execute()` method is called with the `ProbeResult` from the `SourceProber`.
3.  The `DownloadContext` looks at the `mime_type` in the `ProbeResult` and uses its internal `_strategy_map` to find the corresponding strategy class (e.g., `"application/gzip"` maps to `GzipRegime`).
4.  It instantiates the chosen strategy.
5.  It determines the destination file path and creates the necessary directories.
6.  It calls the strategy's `download()` method, which performs the actual download and returns the file's SHA-256 hash.
7.  Finally, it bundles the file path, size, hash, and timing information into a `DownloadEvent` object and returns it.

## 2. `DownloadContext` Class

**Purpose:** To orchestrate the download process by selecting and executing the correct download strategy.

**Key Methods:**
-   `__init__(self, path_manager: PathManager)`: Initializes the context with a `PathManager` instance to handle file system operations.
-   `execute(self, probe_result: ProbeResult, source: ETLSource, conf: ETLConfig) -> DownloadEvent`: The main method that drives the download process and returns a `DownloadEvent`.

## 3. `GzipRegime` Class

**Purpose:** To provide a specific implementation for downloading gzip files.

**Key Methods:**
-   `download(self, url: str, destination: Path, client: httpx.Client) -> str`: Streams the content from the given `url` using the provided `httpx.Client`. It calculates the SHA-256 hash of the content *while streaming* to minimize memory usage and writes the file to the `destination` path in chunks. It returns the final SHA-256 hexdigest.

## 4. `DownloadEvent` Model

This immutable Pydantic model is the successful result of a download operation.

| Field | Type | Description |
| :-- | :--- | :--- |
| `file_path` | `FilePath` | A Pydantic type that validates the file exists at the given path. |
| `file_size_bytes`| `int` | The size of the downloaded file in bytes. Must be greater than 0. |
| `sha256` | `str` | The 64-character SHA-256 hexdigest of the file content. |
| `ts_download_started`| `AwareDatetime`| A timezone-aware timestamp of when the download began. |
| `ts_download_completed`| `AwareDatetime`| A timezone-aware timestamp of when the download finished. |
| `download_regime`| `str` | The name of the `DownloadStrategy` class used (e.g., "GzipRegime"). |

## 5. Usage Example

```python
# Assuming 'probe_result', 'source', 'config', and 'path_manager' are available
from etl.src.extractor.download.context import DownloadContext

# 1. Initialize the context
download_context = DownloadContext(path_manager=path_manager)

# 2. Execute the download
# This will automatically select the GzipRegime based on the probe_result
try:
    download_event = download_context.execute(
        probe_result=probe_result,
        source=source,
        conf=config
    )
    print(f"Download successful!")
    print(f"  File: {download_event.file_path}")
    print(f"  SHA256: {download_event.sha256}")

except ValueError as e:
    print(f"Download failed: {e}") # e.g., No strategy found for MIME type

```
