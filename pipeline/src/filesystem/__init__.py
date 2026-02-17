# --- Libraries ---
from dataclasses import asdict
# --- Dependencies ---
from ..config import settings

# --- Package ---
from .registry import FilesystemRegistry
from .adapters import FilesystemAdapter

# Assemble Dependency
directory_map = settings.dir.model_dump()
_registry_instance = FilesystemRegistry(directory_map)

# Instantiate Singleton
Filesystem = FilesystemAdapter(_registry_instance)

__all__ = ["Filesystem"]