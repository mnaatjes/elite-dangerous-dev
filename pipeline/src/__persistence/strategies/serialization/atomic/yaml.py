# src/persistence/strategies/serialization/atomic/yaml.py

import yaml
from typing import Any, Union
from ..abstracts import AtomicSerializer

class AtomicYAMLSerializer(AtomicSerializer):
    NAME = "yaml"
    
    def encode(self, data: Any) -> str:
        return yaml.dump(data, default_flow_style=False)

    def decode(self, payload: Union[str, bytes]) -> Any:
        return yaml.safe_load(payload)