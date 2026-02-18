from abc import ABC, abstractmethod
from typing import Any, Union

class SerializerStrategy(ABC):
    """
    Purpose: To encode/decode entire Python objects into a storage-ready 
    format (JSON, Binary, etc.) in a single operation.

    Do's and Don'ts:
    - SHOULD handle infrastructure-level formatting (e.g., dict to JSON).
    - SHOULD NOT perform business logic or domain-specific transformation.
    """

    @abstractmethod
    def encode(self, data: Any) -> Union[str, bytes]:
        """Encodes a Python object into a formatted string or bytes."""
        pass

    @abstractmethod
    def decode(self, payload: Union[str, bytes]) -> Any:
        """Decodes a formatted string or bytes back into a Python object."""
        pass