from typing import Any

from ..const import Capability
from .abstracts import StreamingIntegrity, AtomicIntegrity
from ..const import Capability, Category


# Inherit from BOTH to satisfy all type guards
class NoOpIntegrity(AtomicIntegrity, StreamingIntegrity):
    NAME = "no_op"
    CATEGORY = Category.INTEGRITY
    CAPABILITIES = Capability.ATOMIC | Capability.STREAM | Capability.APPEND
    IS_ABSTRACT = False

    # --- Atomic Method ---
    def calculate(self, data: bytes) -> str:
        return ""

    # --- Streaming Methods ---
    def update(self, chunk: bytes) -> None:
        pass

    def finalize(self) -> str:
        return ""

    # --- The Missing Contract Methods ---
    def reset(self) -> None:
        """Required by abstract: Clears internal state for reuse."""
        pass

    def validate(self, expected: Any, actual: Any) -> bool:
        """Required by abstract: Standard equality check."""
        return True