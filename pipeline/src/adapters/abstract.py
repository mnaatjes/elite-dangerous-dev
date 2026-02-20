from abc import ABC, abstractmethod
from typing import Any, ContextManager

class AbstractAdapter(ABC):
    """
    Interface for all Storage Providers (Filesystem, DB, Cloud).
    Enforces a 'Target-based' I/O API.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the type of storage (e.g., 'Linux-FS', 'PostgreSQL')."""
        pass
    
    @abstractmethod
    def exists(self, target: str) -> bool:
        """Check if the resource identified by target exists."""
        pass

    @abstractmethod
    def remove(self, target: str) -> None:
        """Delete the resource at the target location."""
        pass

    @abstractmethod
    def get_capacity(self, path: str) -> int:
        """Returns available capacity at a specific resolved location."""
        pass

    @abstractmethod
    def open_text_stream(self, target: str, mode: str) -> ContextManager[Any]:
        """Provides a handle for line-by-line text I/O (e.g., NDJSON)."""
        pass

    @abstractmethod
    def open_bytes_stream(self, target: str, mode: str) -> ContextManager[Any]:
        """Provides a handle for chunked binary I/O (e.g., Gzip/Compressed)."""
        pass

    @abstractmethod
    def write(self, target: str, payload: Any) -> None:
        """Persist the payload to the specific target location."""
        pass

    @abstractmethod
    def read_text(self, target: str) -> str:
        """Explicitly retrieve as a string."""
        pass

    @abstractmethod
    def read_bytes(self, target: str) -> bytes:
        """Explicitly retrieve as raw bytes."""
        pass