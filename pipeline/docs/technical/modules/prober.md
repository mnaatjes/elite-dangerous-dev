# Module: Source Prober

**Source Files:**
-   `src/extractor/source_probe/prober.py`
-   `src/extractor/source_probe/model.py`
-   `src/extractor/source_probe/checksum_metadata.py`

The `SourceProber` acts as the "scout" for the ETL pipeline. Before committing to a full download, it performs a lightweight, exploratory check on a remote URL to gather essential metadata. This prevents wasted bandwidth and allows the application to make intelligent decisions about how (or if) to download the file.

## 1. Architecture

The `SourceProber` is a Pydantic-based service class. It is instantiated with configuration settings and exposes a single primary method, `execute()`. Its sole job is to return a `ProbeResult` data object containing the metadata it discovers.

### How it Works

1.  **HEAD Request:** It first sends an HTTP `HEAD` request to the target URL. This fetches all response headers without downloading the file body. From this, it extracts crucial information like `Content-Length`, `ETag`, and `Last-Modified`.
2.  **Checksum Extraction:** A `ChecksumMetadata` helper class parses the headers to find any and all checksums provided by the server (e.g., ETag, `x-amz-meta-sha256`).
3.  **Partial GET Request:** It then sends a second HTTP `GET` request using a `Range` header to download only the first 1024 bytes of the file.
4.  **Magic Byte Analysis:** It uses the `python-magic` library to analyze this 1KB sample, determining the file's true MIME type from its content signature, not its file extension.
5.  **Return Result:** All collected metadata is packaged into a `ProbeResult` model and returned. If any step fails, the `probe_error` field in the result is populated.

## 2. `SourceProber` Class

**Purpose:** To gather metadata from a remote URL without downloading the entire file.

**Initialization:**
The class is initialized with settings, typically from the `ETLConfig` object.

```python
# Example Initialization
from etl.src.config.model import ETLConfig
from etl.src.extractor.source_probe.prober import SourceProber

config = ETLConfig()
probe = SourceProber(
    user_agent=config.user_agent,
    chunk_size=config.downloads.chunk_size,
    timeout=config.downloads.timeout,
)
```

**Key Methods:**
-   `execute(self, url: str) -> ProbeResult`: The main method. Takes a URL string and performs the probing logic, returning a `ProbeResult` object.

## 3. `ProbeResult` Model

This Pydantic model is the data container for the outcome of a probing operation.

| Field | Type | Description |
| :-- | :--- | :--- |
| `url` | `str` | The URL that was probed. |
| `status_code` | `int` | The HTTP status code from the initial HEAD request. `0` indicates a connection error. |
| `content_length`| `int \| None`| The file size in bytes, from the `Content-Length` header. |
| `etag` | `str \| None`| The ETag header value, used for caching and state checks. |
| `last_modified`| `str \| None`| The `Last-Modified` header value. |
| `mime_type` | `str` | The MIME type as determined by `python-magic`. Defaults to "unknown". |
| `is_range_supported` | `bool` | `True` if the server supports byte-range requests (`Accept-Ranges: bytes`). |
| `checksum_metadata`| `ChecksumMetadata`| A nested model containing all checksums found in the headers. |
| `probe_error` | `str \| None`| If not `None`, contains a string describing the error that occurred. |

## 4. Usage Example

```python
# Assuming 'probe' is an initialized SourceProber instance
source_url = "http://example.com/data/systems.json.gz"

probe_result = probe.execute(url=source_url)

if probe_result.probe_error:
    print(f"Failed to probe {source_url}: {probe_result.probe_error}")
else:
    print(f"Probe successful for {source_url}:")
    print(f"  MIME Type: {probe_result.mime_type}")
    print(f"  ETag: {probe_result.etag}")
    print(f"  Size: {probe_result.content_length} bytes")

# The DownloadContext would then use this 'probe_result'
# to select a download strategy.
```
