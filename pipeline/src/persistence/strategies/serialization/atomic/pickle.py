# src/persistence/strategies/serialization/atomic/pickle.py
import pickle
from typing import Any
from ..abstracts import AtomicSerializer

class AtomicPickleSerializer(AtomicSerializer):
    NAME = "pickle"

    def encode(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def decode(self, payload: bytes) -> Any:
        return pickle.loads(payload)