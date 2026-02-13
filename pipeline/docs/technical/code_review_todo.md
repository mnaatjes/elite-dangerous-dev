
---

## Deeper Review: Additional Findings

This section contains a more fine-grained review, identifying subtler issues related to code clarity, conventions, and potential for bugs.

### 1. Configuration (`src/config/`)

#### `model.py`

-   **[Clarity] Line 13:** The use of `parents[2]` to find the component root is fragile and lacks context. A change in the directory structure would break this "magic number."
    -   **TODO:** Add a comment explaining *why* `parents[2]` is used, or implement a more robust project root discovery mechanism.
-   **[Design] Line 40 (`model_post_init`):** The configuration object automatically creates directories on the filesystem upon initialization. This is an unexpected side effect. Configuration objects should ideally be passive data containers and not perform I/O or modify the filesystem.
    -   **TODO:** Remove the `_ensure_directories` call from `model_post_init` and create an explicit `setup_directories()` method to be called once at the application's entry point.

### 2. Common Modules (`src/common/`)

#### `manifests/manager.py`

-   **[Bug Risk] Line 22:** The singleton's `__init__` re-initialization guard is silent. If `ManifestManager()` is called a second time with different `root_dir` or `etl_version` arguments, the new arguments are ignored without warning, and the old instance is returned. This can lead to very confusing bugs.
    -   **TODO:** The `__init__` guard should check if the new arguments match the existing instance's arguments. If they differ, it should either log a warning or raise a `RuntimeError`.

#### `manifests/model.py`

-   **[Bug Risk] Line 15:** `_registry = {}` is a mutable class attribute. If the `Manifest` class were ever subclassed, the child and parent would share the same registry dictionary, leading to unexpected behavior and state pollution.
    -   **TODO:** While not currently subclassed, a safer pattern is to manage the registry on a separate factory or within the `ManifestManager` itself, not on the `Manifest` base class.
-   **[Design] Line 31:** The `__init__` method has a high number of responsibilities (validation, path creation, auto-loading from disk). This makes the class harder to test in isolation without hitting the filesystem.
    -   **TODO:** Consider separating the file loading (`load()`) into an explicit method that is called by the factory (`ManifestManager`) after instantiation, rather than automatically in the constructor.

#### `manifests/record.py`

-   **[Performance] Line 41 (`file_size_actual`):** This is implemented as a `@property`, which hides the fact that it performs a filesystem I/O operation (`.stat()`). If this property is accessed frequently in a loop, it can cause a significant performance bottleneck.
    -   **TODO:** Rename this to a method, e.g., `get_actual_file_size()`, to make the I/O operation explicit to the caller.

### 3. Extractor (`src/extractor/`)

#### `source_probe/prober.py`

-   **[Code Smell] Line 17:** The `model_post_init` method is empty and unused.
    -   **TODO:** Remove the empty `model_post_init` method.
-   **[Incomplete Feature] Line 38, 41:** The code contains `TODO` comments indicating that the `range_supported` flag is not used and a "version" property is not being grabbed from the header. This represents dead code or incomplete features.
    -   **TODO:** Either implement the logic to utilize these values or remove the code and comments to clean up the module.
-   **[Clarity] `execute` method:** This method is long and handles multiple network requests and logic steps.
    -   **TODO:** Refactor the `execute` method by breaking its logic into smaller private methods (e.g., `_probe_headers`, `_probe_content_sample`) to improve readability and separation of concerns.

#### `download/context.py`

-   **[Hardcoded Value] Line 28:** `process="FULL"` is a hardcoded "magic string."
    -   **TODO:** Define this value as a constant or an enum member within `common/constants.py` to improve maintainability.

#### `download/regimes/gzip.py`

-   **[Hardcoded Value] Line 12:** `chunk_size=128 * 1024` is a hardcoded magic number. This prevents tuning the chunk size from the application's configuration.
    -   **TODO:** The `download` method should accept `chunk_size` as an argument, which the `DownloadContext` can provide from the `ETLConfig` object.
