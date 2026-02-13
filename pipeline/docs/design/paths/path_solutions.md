# Path Management Solutions and Design Patterns

This document proposes a new design for a centralized `PathManager` class to address the issues identified in the `path_analysis.md` document. The goal is to create a single, robust, and flexible component for all filesystem interactions within the ETL pipeline.

## 1. Core Principles

The new `PathManager` will be designed around the following principles:

- **Single Responsibility Principle:** The `PathManager` will be the *only* class responsible for path resolution, directory creation, and file I/O. Other classes will delegate these tasks to the `PathManager`.
- **Configuration Driven:** All base paths will be derived from the central `ETLConfig` object. This eliminates hardcoded paths and makes the system more flexible.
- **Explicit is Better than Implicit:** Filesystem modifications (like creating directories or writing files) will be performed through explicit method calls, not as hidden side-effects of other operations.
- **Abstraction:** The `PathManager` will provide a high-level API that abstracts away the details of the underlying filesystem structure. Consumers of the class will ask for "the manifest directory" or "a new download file path," not construct paths manually.

## 2. Proposed `PathManager` Class Design

The new `PathManager` will be a stateful service, initialized with the `ETLConfig` object. It will provide a comprehensive set of methods for managing all paths and files used by the application.

### 2.1. Initialization

```python
from pathlib import Path
from etl.src.config.model import ETLConfig

class PathManager:
    def __init__(self, config: ETLConfig):
        self.config = config
        self._root = config.root_dir

        # Adjust root for testing environments
        if config.orchestration.testing_mode:
            self._root = self._root / "tests"
            
        # Ensure the root directory exists
        self._ensure_dir(self._root)

    def _ensure_dir(self, path: Path):
        """Ensures a directory exists, creating it if necessary."""
        path.mkdir(parents=True, exist_ok=True)
```

**Design Choices:**

- **Dependency Injection:** The `PathManager` is initialized with the `ETLConfig` object, making it easy to access all configuration-defined paths. This follows the Dependency Inversion Principle.
- **Testing Environment Handling:** The logic for adjusting the root path during testing is now centralized in the `PathManager`'s constructor.

### 2.2. Path Resolution Methods

These methods will provide paths to the key directories used by the ETL pipeline. They will not have any side-effects (i.e., they won't create the directories).

```python
    def get_root_dir(self) -> Path:
        """Returns the root directory for the current environment."""
        return self._root

    def get_downloads_dir(self) -> Path:
        """Returns the path to the main downloads directory."""
        return self._root / self.config.downloads.destination_dir

    def get_manifests_dir(self) -> Path:
        """Returns the path to the manifest storage directory."""
        return self._root / self.config.downloads.manifest_dir

    def get_raw_data_dir(self) -> Path:
        """Returns the path to the raw data directory."""
        return self._root / self.config.downloads.raw_dir
```

### 2.3. Path and Filename Generation

These methods will handle the logic for creating new, unique file paths.

```python
    from datetime import datetime
    import re

    def new_download_path(self, source_id: str, process: str, dataset: str, version: str, extension: str) -> Path:
        """
        Generates a new, timestamped path for a downloaded file.
        Example: .../downloads/2026/02/spansh_systems_FULL_20260213_190626_v1-0.json.gz
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Sanitize version string
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '-')

        filename = f"{source_id}_{dataset}_{process}_{timestamp}_v{safe_version}{extension}"
        
        # Create path with YYYY/MM structure
        download_dir = self.get_downloads_dir() / now.strftime("%Y") / now.strftime("%m")
        self._ensure_dir(download_dir) # Ensure the subdirectory exists
        
        return download_dir / filename

    def get_manifest_path(self, process_name: str, version: str) -> Path:
        """
        Generates the path for a manifest file.
        Example: .../manifests/downloads_v1-0.json
        """
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '-')
        filename = f"{process_name.lower()}_v{safe_version}.json"
        manifest_dir = self.get_manifests_dir()
        self._ensure_dir(manifest_dir)
        return manifest_dir / filename
```

### 2.4. File I/O Methods

These methods will encapsulate all file reading and writing operations.

```python
    import json

    def read_json(self, path: Path) -> any:
        """Reads and parses a JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Handle gracefully
            return None 
        except json.JSONDecodeError as e:
            # Handle malformed JSON
            raise ValueError(f"Error decoding JSON from {path}: {e}")

    def write_json(self, path: Path, data: any, atomic: bool = True):
        """
        Writes data to a JSON file.
        If atomic is True, uses a temporary file to prevent corruption.
        """
        if atomic:
            temp_path = path.with_suffix(f"{path.suffix}.tmp")
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=4, default=str)
            temp_path.replace(path)
        else:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4, default=str)
```

## 3. Design Patterns

- **Facade Pattern:** The `PathManager` will act as a facade, providing a simple, unified interface to the complex and varied filesystem operations required by the application.
- **Strategy Pattern:** For file I/O, the `PathManager` could be extended to use different strategies for different file types (e.g., a `JsonStrategy`, a `GzipStrategy`). For now, we will implement the JSON methods directly.
- **Singleton (or Application-Scoped Instance):** The `PathManager` should be instantiated once per application run and shared across all components that need it. This can be achieved by creating an instance in the main application entry point and passing it down, or by using a dependency injection container.

## 4. Benefits of the New Design

- **Consistency:** All path and file operations will be handled in a single, consistent way.
- **Robustness:** Centralizing logic makes it easier to implement error handling, logging, and features like atomic writes.
- **Maintainability:** Changes to the directory structure or file naming conventions will only need to be made in one place.
- **Testability:** The `PathManager` can be easily mocked or subclassed in tests to create a virtual filesystem, allowing for more robust and isolated unit tests.
- **Decoupling:** Application components will be decoupled from the specifics of the filesystem, making the codebase more modular and easier to refactor.
