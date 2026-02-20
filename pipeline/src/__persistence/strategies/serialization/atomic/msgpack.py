# src/persistence/strategies/serialization/atomic/msgpack.py
import msgpack
from typing import Any, cast # Add cast here
from ..abstracts import AtomicSerializer

class AtomicMsgPackSerializer(AtomicSerializer):
    NAME = "msgpack"

    def encode(self, data: Any) -> bytes:
        # cast tells the type checker "I guarantee this is bytes"
        return cast(bytes, msgpack.packb(data, use_bin_type=True))

    def decode(self, payload: bytes) -> Any:
        return msgpack.unpackb(payload, raw=False)