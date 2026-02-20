# src/persistence/strategies/serialization/stateful/ndjson.py

import json
from typing import Any, Union
from ..abstracts import StreamingSerializer

class NDJsonSerializer(StreamingSerializer):
    NAME = "ndjson"

    def encode_item(self, item: Any) -> str:
        # Use separators for compact JSON (removes extra whitespace)
        # This is better for massive Elite Dangerous star-data files
        return json.dumps(item, separators=(',', ':')) + "\n"

    def finalize(self) -> str:
        return ""