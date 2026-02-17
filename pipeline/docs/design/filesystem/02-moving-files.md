# Moving Files

To handle both "Cross-Registry" moves (from one key to another) and "Internal" moves (within the same key), the `move()` method in the `FilesystemAdapter` accepts a Source (Key + Sub-path) and a Destination (Key + Sub-path).

## The "Double-Key" Move Signature

By requiring a key for both the source and the destination, every move operation is validated against the Registry.

```python
import shutil

def move(self, src_key, src_sub_path, dst_key, dst_sub_path):
    # 1. Resolve both anchors via the Registry
    src_base = self.registry.resolve(src_key)
    dst_base = self.registry.resolve(dst_key)

    # 2. Build the full physical Linux paths
    src_full = src_base / src_sub_path
    dst_full = dst_base / dst_sub_path

    # 3. Safety First: Ensure destination directory exists
    dst_full.parent.mkdir(parents=True, exist_ok=True)

    # 4. Perform the atomic move (using shutil for cross-device support)
    shutil.move(str(src_full), str(dst_full))
```

### Use Case 1: Cross-Key Move

Move from `downloads/file.json` to `raw/2026/file.json`.

```python
adapter.move(
    src_key="downloads", src_sub_path="file.json",
    dst_key="raw",       dst_sub_path="2026/file.json"
)
```

The Registry resolves `downloads` to one path and `raw` to another. `shutil.move` works even if `raw` is on a different mount point.

### Use Case 2: Internal Move

Move within the `downloads` directory.

```python
adapter.move(
    src_key="downloads", src_sub_path="file.json",
    dst_key="downloads", dst_sub_path="2026/02/file.json"
)
```

The logic remains identical; the same base path is resolved twice.

### The "Internal Move" Shortcut

For frequent internal moves, `dst_key` can be made optional.

```python
def move(self, src_key, src_sub_path, dst_sub_path, dst_key=None):
    # If dst_key isn't provided, reuse the src_key
    dst_key = dst_key or src_key
    # ... rest of the logic ...
```

## Parameter Grouping: Dictionaries vs. Location Objects

Using a dictionary like `{key: sub_path}` can lead to the "Magic Dictionary" problem, hiding the data structure. Explicit parameters are clearer.

A better alternative for grouping is a `NamedTuple` or `Dataclass`.

```python
from typing import NamedTuple

class FileLocation(NamedTuple):
    key: str
    sub_path: str

# Usage
src = FileLocation("downloads", "file.json")
dst = FileLocation("raw", "2026/file.json")

adapter.move(src, dst)
```

This provides type hinting, immutability, and a clean method signature.

### Implementation with Location Objects

```python
def move(self, src: FileLocation, dst: FileLocation):
    # Resolve the physical paths using the Registry
    src_path = self.registry.resolve(src.key) / src.sub_path
    dst_path = self.registry.resolve(dst.key) / dst.sub_path
    
    # Perform the move
    shutil.move(str(src_path), str(dst_path))
```
