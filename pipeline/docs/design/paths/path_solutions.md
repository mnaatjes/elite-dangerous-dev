# Path Management Solutions and Design Patterns

This document proposes a new design for a centralized `PathManager` class to address the issues identified in the `path_analysis.md` document. The goal is to create a single, robust, and flexible component for all filesystem interactions within the ETL pipeline.

## 1. Core Principles

The new `PathManager` will be designed around the following principles:

- **Single Responsibility Principle:** The `PathManager` will be the *only* class responsible for path resolution, directory creation, and file I/O. Other classes will delegate these tasks to the `PathManager`.
- **Configuration Driven:** All base paths will be derived from the central `ETLConfig` object. This eliminates hardcoded paths and makes the system more flexible.
- **Explicit is Better than Implicit:** Filesystem modifications (like creating directories or writing files) will be performed through explicit method calls, not as hidden side-effects of other operations.
- **Abstraction:** The `PathManager` will provide a high-level API that abstracts away the details of the underlying filesystem structure. Consumers of the class will ask for "the manifest directory" or "a new download file path," not construct paths manually.

## 2. Method Naming Conventions

To ensure the behavior of the `PathManager` is always clear and predictable, all methods will adhere to a strict naming convention based on their function. This clarifies the distinction between methods that simply return a `Path` object and those that perform I/O operations on the filesystem.

| Prefix | Action | I/O | Example |
| :--- | :--- | :-: | :--- |
| `get_*` | Returns a `Path` object for a directory or file. Never creates anything. | **No** | `get_root_dir()` |
| `generate_*` | Composes and returns a new, often unique, `Path` object. Never creates it. | **No** | `generate_download_path()` |
| `create_*` | Actively creates something on the filesystem (e.g., a directory). | **Yes** | `create_directory()` |
| `read_*` | Reads data from a file. | **Yes** | `read_json()` |
| `write_*` | Writes data to a file. | **Yes** | `write_json()` |

## 3. Proposed `PathManager` Class Design

The new `PathManager` will be a stateful service, initialized with the `ETLConfig` object. It will provide a comprehensive set of methods for managing all paths and files used by the application.

### 3.1. Initialization

```python
from pathlib import Path
from etl.src.config.model import ETLConfig
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar
import json
import re
from datetime import datetime

# TypeVar allows for correct type hinting with any Pydantic model class
T = TypeVar('T', bound=BaseModel)


class PathManager:
    def __init__(self, config: ETLConfig):
        self.config = config
        self._root = config.root_dir

        # Adjust root for testing environments
        if config.orchestration.testing_mode:
            self._root = self._root / "tests"
            
        # The root directory is NOT created on initialization.
        # This is the responsibility of the application's startup logic.

    def create_directory(self, path: Path):
        """Ensures a directory exists, creating it and any parents if necessary."""
        path.mkdir(parents=True, exist_ok=True)
```

**Design Choices:**

- **Dependency Injection:** The `PathManager` is initialized with the `ETLConfig` object, making it easy to access all configuration-defined paths.
- **No I/O in Constructor:** The constructor does not perform any filesystem operations. It is side-effect free, making the class more predictable and easier to test.
- **Explicit Directory Creation:** A public `create_directory()` method is provided for explicitly creating directories.

### 3.2. Path Resolution Methods (`get_*`)

These methods provide paths to the key directories used by the ETL pipeline. They do not have any side-effects (i.e., they won't create the directories).

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

### 3.3. Path and Filename Generation (`generate_*`, `get_*`)

These methods handle the logic for creating new, unique file paths. They strictly adhere to the "no side-effects" rule.

```python
    def generate_download_path(self, source_id: str, process: str, dataset: str, version: str, extension:str) -> Path:
        """
        Generates a new, timestamped path for a downloaded file.
        Example: .../downloads/2026/02/spansh_systems_FULL_20260213_190626_v1-0.json.gz
        
        NOTE: This method does NOT create the directory. The caller must explicitly
        create it using create_directory(path.parent).
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Sanitize version string
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '-')

        filename = f"{source_id}_{dataset}_{process}_{timestamp}_v{safe_version}{extension}"
        
        # Create path with YYYY/MM structure
        download_dir = self.get_downloads_dir() / now.strftime("%Y") / now.strftime("%m")
        
        return download_dir / filename

    def get_manifest_path(self, process_name: str, version: str) -> Path:
        """
        Generates the path for a manifest file.
        Example: .../manifests/downloads_v1-0.json

        NOTE: This method does NOT create the directory.
        """
        safe_version = re.sub(r'[^\w-]', '', version).replace('.', '-')
        filename = f"{process_name.lower()}_v{safe_version}.json"
        manifest_dir = self.get_manifests_dir()
        return manifest_dir / filename
```

### 3.4. File I/O Methods

These methods encapsulate all file reading and writing operations, providing both low-level and high-level interfaces.

#### Generic JSON I/O

```python
    def read_json(self, path: Path) -> any:
        """Reads and parses a JSON file into a raw Python object (dict or list)."""
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
        Writes a raw Python object to a JSON file. The parent directory must exist.
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

#### Pydantic Model I/O

```python
    def read_pydantic_model(self, path: Path, model_class: Type[T]) -> T | None:
        """
        Reads a JSON file and validates its contents into a Pydantic model.
        Returns the model instance or None if the file doesn't exist.
        Raises ValueError on validation or JSON decoding errors.
        """
        raw_data = self.read_json(path) # Use our existing low-level reader
        if raw_data is None:
            return None
        
        try:
            # Pydantic handles all nested validation automatically!
            return model_class.model_validate(raw_data)
        except ValidationError as e:
            raise ValueError(f"Pydantic validation failed for {path}: {e}")

    def write_pydantic_model(self, path: Path, model: BaseModel, atomic: bool = True):
        """
        Writes a Pydantic model to a JSON file.
        The parent directory must exist.
        """
        # Pydantic can dump the model to a JSON-compatible dictionary
        data_to_write = model.model_dump(mode='json')
        self.write_json(path, data_to_write, atomic) # Use our existing low-level writer
```

## 4. Design Patterns

- **Facade Pattern:** The `PathManager` will act as a facade, providing a simple, unified interface to the complex and varied filesystem operations required by the application.
- **Strategy Pattern:** For file I/O, the `PathManager` could be extended to use different strategies for different file types (e.g., a `JsonStrategy`, a `GzipStrategy`). For now, we will implement the JSON methods directly.
- **Singleton (or Application-Scoped Instance):** The `PathManager` should be instantiated once per application run and shared across all components that need it. This can be achieved by creating an instance in the main application entry point and passing it down, or by using a dependency injection container.

## 5. Benefits of the New Design

- **Consistency:** All path and file operations will be handled in a single, consistent way, enforced by the naming convention.
- **Predictability:** The behavior of methods is clear from their names. There are no hidden side-effects.
- **Robustness:** Centralizing logic makes it easier to implement error handling, logging, and features like atomic writes.
- **Maintainability:** Changes to the directory structure or file naming conventions will only need to be made in one place.
- **Testability:** The `PathManager` can be easily mocked. Because the constructor is side-effect free, it's trivial to instantiate in unit tests.
- **Decoupling:** Application components will be decoupled from the specifics of the filesystem, making the codebase more modular and easier to refactor.
