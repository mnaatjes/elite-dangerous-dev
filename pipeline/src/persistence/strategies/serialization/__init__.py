# persistence/strategies/serialization/__init__.

from .abstract import SerializerStrategy
from .json import JsonSerializer

__all__ = [
    "SerializerStrategy",
    "JsonSerializer"
]