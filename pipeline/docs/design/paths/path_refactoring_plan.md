# Path Management Refactoring Plan

This document provides a step-by-step plan for refactoring the ETL pipeline's codebase to adopt the new, centralized `PathManager` as proposed in `path_solutions.md`.

## 1. Objective

The goal of this refactoring is to eliminate all direct filesystem access from application components and delegate these responsibilities to a single, unified `PathManager`. This will improve the codebase's consistency, robustness, and maintainability.

## 2. Refactoring Phases

The refactoring process will be broken down into the following phases:

### Phase 1: Implement the New `PathManager`

1.  **Create the `PathManager` class:**
    *   Create a new file: `etl/src/common/path_manager.py`.
    *   Implement the `PathManager` class as designed in `path_solutions.md`.
    *   This includes the constructor, path resolution methods, path generation methods, and file I/O methods.
2.  **Add Unit Tests:**
    *   Create a corresponding test file: `etl/tests/common/test_path_manager.py`.
    *   Write unit tests for the `PathManager` class. Use mocking to inject a `MagicMock` of `ETLConfig` to test the path resolution logic under different configurations (e.g., `testing_mode`).
    *   Use the `unittest.mock.patch` decorator to mock `open` and `pathlib.Path` to test file I/O methods without touching the actual filesystem.

### Phase 2: Integrate `PathManager` into the Application

1.  **Instantiate `PathManager`:**
    *   In the main application entry point (likely `etl/main.py`), instantiate the `ETLConfig` object.
    *   Then, create a single instance of the `PathManager`, passing the config object to its constructor.
    ```python
    # etl/main.py
    from etl.src.config.model import ETLConfig
    from etl.src.common.path_manager import PathManager

    def main():
        # 1. Initialize Config
        config = ETLConfig()

        # 2. Initialize PathManager
        path_manager = PathManager(config)

        # ... rest of the application logic
    ```
2.  **Dependency Injection:**
    *   Pass the `path_manager` instance to all top-level components that require filesystem access. This will likely involve updating the constructors of classes like `DownloadContext`, `SourcesManager`, and `Manifest`.

### Phase 3: Refactor Individual Components

For each of the components identified in the analysis, perform the following steps:

#### `etl/src/config/model.py` (`ETLConfig`)

1.  **Remove `_ensure_directories`:** Delete this method. Directory creation is no longer the responsibility of the config class.
2.  **Remove `_resolve_full_path` and related getters:** Delete `_resolve_full_path`, `get_downloads_dir`, `get_manifests_dir`, and `get_raw_dir`. Path resolution will be handled by the `PathManager`.

#### `etl/src/common/manifests/model.py` (`Manifest`)

1.  **Update Constructor:** Modify the `__init__` method to accept a `PathManager` instance.
2.  **Refactor Path Construction:** Replace the manual path construction with a call to `path_manager.get_manifest_path()`.
3.  **Refactor `save` method:**
    *   Remove the `with open(...)` block.
    *   Call `path_manager.write_json(self.path, output_data)`.
4.  **Refactor `load` method:**
    *   Remove the `with open(...)` block.
    *   Call `data = path_manager.read_json(self.path)`.

#### `etl/src/extractor/sources/source_manager.py` (`SourcesManager`)

1.  **Update Constructor:** Modify `__init__` to accept a `PathManager` and the `sources_filepath` from the config.
2.  **Refactor `load_from_file`:**
    *   Replace the `with open(...)` block with a call to `data = self.path_manager.read_json(self.file_path)`.
3.  **Refactor `save_sources`:**
    *   Replace the `with open(...)` block with a call to `self.path_manager.write_json(self.file_path, output)`.

#### `etl/src/extractor/download/context.py` (`DownloadContext`)

1.  **Update `_generate_filename`:** This method can be completely removed.
2.  **Update `execute` method:**
    *   Replace the call to `_generate_filename` and subsequent path resolution with a single call to `self.path_manager.new_download_path(...)`.

#### `etl/src/common/config.py` (`Config`) - DEPRECATION

This class appears to be an older implementation of configuration management. The `etl.config.json` and the pydantic-based `ETLConfig` seem to be two different ways of handling configuration.

1.  **Analysis:** Determine if `Config` is still in use. If so, it should be deprecated and replaced with `ETLConfig`.
2.  **Refactoring:**
    *   Replace all usages of the singleton `Config()` with the `ETLConfig` instance that is passed down through dependency injection.
    *   Remove the `etl/src/common/config.py` file.
    *   Remove `etl/etl.config.json` if it's no longer needed, or migrate its values to the `.env` file used by `ETLConfig`.

### Phase 4: Verification

1.  **Run All Tests:** Execute the entire test suite to ensure that the refactoring has not introduced any regressions.
2.  **Manual Testing:** Perform a full run of the ETL pipeline to verify that all components are working correctly with the new `PathManager`. Check that files and directories are created in the expected locations with the correct content.
3.  **Code Review:** Conduct a final code review to ensure that all direct filesystem access has been removed from the refactored components and that the new `PathManager` is used consistently.

## 3. Rollback Plan

If significant issues are discovered during the verification phase, the refactoring can be rolled back by reverting the changes in the version control system (Git). Since the changes are localized to path and file handling, a rollback should be a straightforward process.
