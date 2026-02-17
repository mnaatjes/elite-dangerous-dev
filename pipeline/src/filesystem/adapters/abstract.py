from abc import ABC, abstractmethod
from typing import Any

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
    def write(self, target: str, payload: Any) -> None:
        """Persist the payload to the specific target location."""
        pass

    @abstractmethod
    def read(self, target: str) -> Any:
        """Retrieve the payload from the specific target location."""
        pass

    @abstractmethod
    def remove(self, target: str) -> None:
        """Delete the resource at the target location."""
        pass