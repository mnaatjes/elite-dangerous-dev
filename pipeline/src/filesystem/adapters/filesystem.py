# --- Libraries ---
from pathlib import Path
import shutil

# --- Dependencies ---
from .abstract import AbstractAdapter
from ..registry import FilesystemRegistry

class FilesystemAdapter(AbstractAdapter):
    # For singleton implementation
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Check for instance
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, filesystem_registry:FilesystemRegistry|None = None) -> None:
        # Check for initialization
        if not hasattr(self, '_initialized'):
            # Validate dependency
            if filesystem_registry is None:
                raise ValueError(f"Filesystem Adapter MUST be initialized with a Registry")
            
            # Assign registry
            self._registry = filesystem_registry

            # Initialize
            self._initialized = True

    # --- Abstraction Method Implementations ---
    @property
    def provider_name(self) -> str:
        return "Linux-Filesystem"

    def resolve(self, target:str) -> Path:
        """
        Translates a logical target (filepath) into a pysical disk location
        
        Args:
            target (str): the full path to be translated
        
        Returns:
        """
        key, sub_path = self._split_target(target)
        
        # 1. Ask the Registry for the anchored root (e.g., /data/downloads/)
        anchor = self._registry.get_anchor(key)
        
        # 2. Join with the remaining path
        # Ensure a path is returned even if it is just the anchor path
        return anchor / sub_path if sub_path else anchor

    # --- Public API Methods ---

    def exists(self, target: str) -> bool:
        """Check if a logical target exists on disk."""
        return self.resolve(target).exists()

    def mkdir(self, target: str):
        """Creates the directory structure for a target."""
        path = self.resolve(target)
        path.mkdir(parents=True, exist_ok=True)

    def move(self, src_target: str, dst_target: str):
        """Moves data from one logical target to another."""
        src_full = self.resolve(src_target)
        dst_full = self.resolve(dst_target)

        dst_full.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_full), str(dst_full))

    def remove(self, target: str):
        """Safely deletes a file or directory target."""
        # 1. Resolve to absolute for the Sandbox Guard
        physical_path = self.resolve(target).resolve()
        
        # 2. Extract key to find the authorized anchor
        key, _ = self._split_target(target)
        anchor = self._registry.get_anchor(key).resolve()

        # 3. Path Traversal Guard
        if not str(physical_path).startswith(str(anchor)):
            raise PermissionError("Target is outside the authorized sandbox.")

        # 4. Execute
        if physical_path.is_dir():
            shutil.rmtree(physical_path)
        elif physical_path.is_file():
            physical_path.unlink()

    # --- I/O Methods: Write ---

    def write_text(self, target: str, payload: str):
        """The primary I/O method for the Persistence Orchestrator."""
        path = self.resolve(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload)

    def write(self, target:str, payload:str):
        #raise ModuleNotFoundError("Method 'write' is incomplete!")
        return self.write_text(target, payload)
    
    # --- I/O Methods: Read ---

    def read(self, target:str):
        pass

    # --- Helper Methods ---
    
    def _split_target(self, target:str) -> tuple[str, str]:
        """
        Internal translator from physical path to key, path
        """
        # Ensure no leading slashes
        clean_target = target.lstrip("/")
        
        if "/" not in clean_target:
            # Fallback: Treat the whole string as the key if no sub-dirs exist
            return clean_target, ""
            
        # Split on the FIRST slash only
        key, sub_path = clean_target.split("/", 1)
        return key, sub_path
        pass