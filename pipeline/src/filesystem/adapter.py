from pathlib import Path
import shutil
from .registry import FilesystemRegistry

class FilesystemAdapter:
    # For singleton implementation
    _instance = None

    def __new__(cls, **args):
        # Check for instance
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, filesystem_registry:FilesystemRegistry) -> None:
        # Check for initialization
        if not hasattr(self, '_initialized'):
            # Add dependnecies
            self._registry = filesystem_registry

            # Initialize
            self._initialized = True


    def get_path(self, key:str, sub_path:str|None=None) -> Path:
        # Check base in registry
        # Form full path and return
        base = self._registry.resolve(key)
        
        # Except
        if not base:
            raise KeyError(f"Path '{base}' is NOT Registered in the Filesystem Adapter")
        
        # Return Composed Path
        return base / sub_path if sub_path else base

    def exists(self, key:str, sub_path:str|None=None):
        # The action: Check the physical disk
        return self.get_path(key, sub_path).exists()

    def mkdir(self, key:str):
        # Limits dir creation to those in the registry
        path = self.get_path(key)
        path.mkdir(parents=True, exist_ok=True)

    def move(self, src_key, src_sub_path, dst_key, dst_sub_path):
        # 1. Resolve both anchors via the Registry
        src_base = self._registry.resolve(src_key)
        dst_base = self._registry.resolve(dst_key)

        # 2. Build the full physical Linux paths
        src_full = src_base / src_sub_path
        dst_full = dst_base / dst_sub_path

        # 3. Safety First: Ensure destination directory exists
        dst_full.parent.mkdir(parents=True, exist_ok=True)

        # 4. Perform the atomic move (using shutil for cross-device support)
        shutil.move(str(src_full), str(dst_full))

    def remove(self, key:str, sub_path:str):
        # 1. Protection: Ensure we aren't deleting the root of the key
        if not sub_path or sub_path in ["/", "."]:
            raise ValueError(f"Refusing to delete the root of the '{key}' directory.")

        # 2. Resolve the path safely
        base_path = self._registry.resolve(key)
        target = (base_path / sub_path).resolve()

        # 3. Path Traversal Guard: Ensure target is STILL inside the base
        if not str(target).startswith(str(base_path.resolve())):
            raise PermissionError("Deletion target is outside the authorized sandbox.")

        # 4. Execute (Using shutil for recursive directory deletion)
        import shutil
        if target.is_dir():
            shutil.rmtree(target)
        elif target.is_file():
            target.unlink()

    def write_bytes(self):
        pass