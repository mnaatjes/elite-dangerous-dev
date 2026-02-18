from abc import ABC, abstractmethod
from typing import Any, Union

class SerializerStrategy(ABC):
    """
    Purpose: To turn py dictionary into a formatted string | binary

    Do's and Don'ts: 
    - SerializerStrategy should only care about Data Transformation (Dict -> String/Bytes)

    """
    @abstractmethod
    def serialize(self, data: Any) -> Union[str, bytes]:
        """Converts Python objects into a formatted string (e.g., JSON, XML, YAML)."""
        pass

    @abstractmethod
    def deserialize(self, payload: Union[str, bytes]) -> Any:
        """Parses a formatted string back into Python objects."""
        pass