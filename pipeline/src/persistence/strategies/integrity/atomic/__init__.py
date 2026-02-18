# persistence/strategies/integrity/atomic/__init__.py
from .sha256 import AtomicSha256Strategy

__all__ = [
    "AtomicSha256Strategy"
]