import json
from typing import Any, Union
from ..abstracts import AtomicSerializer

class AtomicJSONSerializer(AtomicSerializer):
    NAME = "json"
    """
    Concrete strategy for JSON serialization.
    Handles the conversion of Python dicts/lists to JSON strings.
    """
    def encode(self, data: Any) -> str:
        """Returns a JSON string. The Adapter will handle disk encoding."""
        return json.dumps(data, indent=4) if data else "{}"

    def decode(self, payload: str) -> Any:
        return json.loads(payload)