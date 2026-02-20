# src/persistence/strategies/integrity/stateful/sha256.py
import hashlib
from typing import Any, Optional
from ..abstracts import StreamingIntegrity
from ...const import Capability, Category

class StreamingSha256Strategy(StreamingIntegrity):
    NAME = "sha256_stream"
    CATEGORY = Category.INTEGRITY
    CAPABILITIES = Capability.STREAM | Capability.APPEND
    IS_ABSTRACT = False

    def __init__(self):
        self._hash = hashlib.sha256()

    def update(self, chunk: bytes) -> None:
        """Adds a chunk of bytes to the rolling checksum."""
        self._hash.update(chunk)

    def finalize(self) -> str:
        """Returns the final hex digest as a string."""
        return self._hash.hexdigest()

    def reset(self) -> None:
        """Clears the hash for a new operation."""
        self._hash = hashlib.sha256()

    def validate(self, expected: str, actual: str) -> bool:
        """Standard hex string comparison."""
        return expected.strip().lower() == actual.strip().lower()