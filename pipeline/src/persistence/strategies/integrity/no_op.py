from ..const import Capability
from .abstracts import StreamingIntegrity
from ..const import Capability, Category

class NoOpIntegrity(StreamingIntegrity):
    NAME = "no_op"
    CATEGORY = Category.INTEGRITY
    # Works for everything because it does nothing.
    CAPABILITIES = Capability.ATOMIC | Capability.STREAM | Capability.APPEND

    def calculate(self, payload) -> str: return ""
    def validate(self, payload, expected) -> bool: return True
    def update(self, chunk) -> None: pass
    def finalize(self) -> str: return ""
    def reset(self) -> None: pass