# Deleting Files

Allowing a `FilesystemAdapter` to delete directories is necessary for cleanup but also dangerous. The best practice is to allow it with heavy structural constraints to prevent accidental data loss. This is achieved through **Scoped Deletion**.

## Deletion Safety Strategies

| Strategy       | Risk Level | Logic                                                |
|----------------|------------|------------------------------------------------------|
| Raw Delete     | 🔴 High    | `shutil.rmtree(any_path)` — A typo could delete `/etc`. |
| Keyed Delete   | 🟡 Medium  | `delete("downloads", "batch_01")` — Safe, but permanent.|
| Soft Delete    | 🟢 Low     | Moves the directory to a `.trash` or `archive` key.  |

## The "Safe Delete" Pattern

The `FilesystemAdapter` should enforce two rules for deletion:
1.  **Must use a Key**: Deletions can only happen inside a registered directory.
2.  **No Root Deletion**: The adapter must refuse to delete the root of a key (e.g., it can delete `downloads/old_batch`, but not the `downloads` folder itself).

```python
import shutil

def delete_subdirectory(self, key, sub_path):
    # 1. Protection: Ensure we aren't deleting the root of the key
    if not sub_path or sub_path in ["/", "."]:
        raise ValueError(f"Refusing to delete the root of the '{key}' directory.")

    # 2. Resolve the path safely
    base_path = self.registry.resolve(key)
    target = (base_path / sub_path).resolve()

    # 3. Path Traversal Guard: Ensure target is STILL inside the base
    if not str(target).startswith(str(base_path.resolve())):
        raise PermissionError("Deletion target is outside the authorized sandbox.")

    # 4. Execute (Using shutil for recursive directory deletion)
    if target.is_dir():
        shutil.rmtree(target)
    elif target.is_file():
        target.unlink()
```

## The "Trash" Pattern

Instead of a "Hard Delete," a `Retention Policy` can be used. The adapter moves the directory to a `trash` key. A separate cron job then deletes anything in trash older than a specified period (e.g., 30 days), providing a safety net.

## Summary Checklist for Deletion

-   **Is it keyed?** (Never delete via raw string).
-   **Is it recursive?** (Use `shutil.rmtree` for folders).
-   **Is it logged?** (A higher-level service should record who deleted what and when).
