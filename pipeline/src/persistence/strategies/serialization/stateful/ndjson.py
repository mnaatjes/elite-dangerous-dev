# src/persistence/strategies/serialization/stateful/ndjson.py

import json
from typing import Any, Union
from ..abstracts import StreamingSerializer

class NDJsonSerializer(StreamingSerializer):
    NAME = "ndjson"
    # Inherits CATEGORY.SERIALIZER and Capability.STREAM from StreamingSerializer

    def encode_item(self, item: Any) -> str:
        """Encodes a single object and adds the Linux newline."""
        return json.dumps(item) + "\n"

    def finalize(self) -> str:
        """NDJSON doesn't need footers, so we return an empty string."""
        return ""