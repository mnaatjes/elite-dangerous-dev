import json
from typing import Any, Union
from ..abstract_atomic import SerializerStrategy

class AtomicJSONSerializer(SerializerStrategy):
    """
    Concrete strategy for JSON serialization.
    Handles the conversion of Python dicts/lists to JSON strings.
    """

    def __init__(self, indent: int = 4):
        self._indent = indent

    def serialize(self, data: Any) -> str:
        """
        Converts Python objects to a JSON-formatted string.
        """
        try:
            return json.dumps(
                data, 
                indent=self._indent, 
                ensure_ascii=False, 
                sort_keys=True
            )
        except (TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to serialize data to JSON: {e}")

    def deserialize(self, payload: Union[str, bytes]) -> Any:
        """
        Converts a JSON string or bytes back into Python objects.
        """
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError) as e:
            raise RuntimeError(f"Failed to deserialize JSON payload: {e}")