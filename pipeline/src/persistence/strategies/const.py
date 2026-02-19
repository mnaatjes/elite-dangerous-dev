# src/persistence/strategies/const.py

from enum import Enum, Flag, auto

class Capability(Flag):
    """Defines what a strategy is physically capable of doing."""
    NONE = 0
    ATOMIC = auto()   # Can process whole objects
    STREAM = auto()   # Can process items/chunks
    APPEND = auto()   # Can safely append to existing files

class Category(Enum):
    SERIALIZER = auto()
    INTEGRITY = auto()
    COMPRESSION = auto()  # Future-proofing for decorators
    ENCRYPTION = auto()   # Future-proofing for decorators