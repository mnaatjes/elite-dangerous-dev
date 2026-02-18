# persistence/strategies/serialization/__init__.

from .abstract_atomic import SerializerStrategy
from .abstract_stateful import StreamingSerializerStrategy
from .atomic import AtomicJSONSerializer, AtomicBinarySerializer


__all__ = [
    "SerializerStrategy",
    # --- Atomic Strategies ---
    "AtomicJSONSerializer",
    "AtomicBinarySerializer",
    # --- Stateful Strategies ---
    "StreamingSerializerStrategy"
]