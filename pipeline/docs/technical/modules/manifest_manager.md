# Module: Manifest System

**Source Files:**
-   `src/common/manifests/manager.py`
-   `src/common/manifests/model.py`
-   `src/common/manifests/record.py`
-   `src/common/manifests/metadata.py`

The manifest system is the state-tracking backbone of the ETL component. It is responsible for creating, managing, and persisting a record of all downloaded files to prevent reprocessing and to provide an audit trail.

## 1. Architecture

The system is composed of two main classes and two supporting Pydantic models:

-   **`ManifestManager`:** A Singleton class that acts as a factory for creating and accessing different `Manifest` instances. It ensures that only one manager object exists.
-   **`Manifest`:** The core class that represents a specific manifest file on disk (e.g., for the `extractor` process). It uses a registry pattern to ensure only one instance per process type is created. It handles all file I/O (loading and atomic saving) and manages the records in memory.
-   **`ManifestMetadata`:** A Pydantic model defining the schema for the `metadata` block within the manifest JSON.
-   **`ManifestRecord`:** A Pydantic model defining the schema for a single file record within the manifest's `records` block.

### How it Works

1.  An instance of `ManifestManager` is created.
2.  To get a specific manifest (e.g., for downloads), you access it as an attribute on the manager: `manager.extractor`.
3.  The `ManifestManager`'s `__getattr__` method intercepts this, validates that `extractor` is a valid `ETLProcess`, and creates/returns a `Manifest` instance for that process.
4.  The `Manifest` instance is stored in a registry, so subsequent calls for `manager.extractor` return the same object.
5.  The `Manifest` object handles loading the corresponding JSON file (e.g., `extractor_v1.0.0.json`) into memory and provides methods to add records and save changes.

## 2. `ManifestManager` Class

**Purpose:** To provide a single, managed entry point for accessing all manifests.

**Key Methods:**
-   `__init__(self, root_dir: str, etl_version: str)`: Initializes the singleton manager with the base directory for all manifests and the current ETL version.
-   `__getattr__(self, name: str)`: Dynamically creates and returns `Manifest` instances based on the attribute name (which must match an `ETLProcess` enum member).

## 3. `Manifest` Class

**Purpose:** To manage the data and file I/O for a single manifest file.

**Key Properties:**
-   `metadata: ManifestMetadata`: The Pydantic model for the manifest's metadata section.
-   `records: Dict[str, ManifestRecord]`: A dictionary holding all file records, keyed by their SHA-256 checksum for efficient lookup.
-   `path: Path`: The full path to the JSON manifest file on disk.

**Key Methods:**
-   `add_record(self, record_params: dict)`: Validates a dictionary of parameters against the `ManifestRecord` model, creates a record object, adds it to the in-memory dictionary, and triggers an atomic save to disk.
-   `save(self)`: Persists the entire manifest (metadata and records) to its JSON file using an atomic "write-then-rename" operation to prevent data corruption.
-   `load(self)`: Reads the JSON file from disk and hydrates the `metadata` and `records` properties with Pydantic model instances.

## 4. `ManifestRecord` Model

This Pydantic model is the "contract" for what constitutes a valid record of a downloaded file.

| Field | Type | Description |
| :-- | :--- | :--- |
| `checksum` | `str` | The SHA-256 hash of the file. Primary key for the records dictionary. |
| `filename` | `str` | The name of the file. |
| `filepath` | `Path` | The absolute path to the file on disk. |
| `etl_version`| `str` | The version of the ETL that produced this record. |
| `is_verified`| `bool` | A flag indicating if a post-download verification check was run. |
| `etag` | `str \| None`| The ETag from the server's HTTP response headers. |
| `content_type`| `str \| None`| The MIME type from the server's HTTP response. |
| `last_modified_server`|`str \| None`| The `Last-Modified` header value from the server. |
| `content_length_bytes`| `int \| None`| The `Content-Length` from the server. |
| `updated_at` | `datetime`| Timestamp of when this record was last updated. |

## 5. Usage Example

```python
from pathlib import Path
from etl.src.common.manifests.manager import ManifestManager
from etl.src.config.model import ETLConfig

# 1. Initialize configuration and manager
config = ETLConfig()
manifest_manager = ManifestManager(
    root_dir=config.get_manifests_dir(),
    etl_version=config.version
)

# 2. Get the manifest for the 'extractor' process
# This will create/load 'extractor_v1.0.0.json'
extractor_manifest = manifest_manager.extractor

# 3. Add a new record (data would typically come from a DownloadEvent)
new_record_data = {
    "checksum": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "filename": "some_file.gz",
    "filepath": Path("/path/to/etl/data/downloads/some_file.gz"),
    "etag": "xyz-etag",
    "content_length_bytes": 12345
}
extractor_manifest.add_record(new_record_data)

# The manifest is now automatically saved to disk.
```
