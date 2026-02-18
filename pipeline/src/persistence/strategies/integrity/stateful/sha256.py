import hashlib
import hmac
from typing import Union
from ..abstract_stateful import StreamingIntegrityStrategy

class StreamingSha256Strategy(StreamingIntegrityStrategy):
    def __init__(self):
        # State maintained for streaming
        self._context = hashlib.sha256()

    # --- Streaming Methods ---
    def update(self, chunk: bytes) -> None:
        self._context.update(chunk)

    def finalize(self) -> str:
        # Returns digest and resets state for the next use
        digest = self._context.hexdigest()
        self._context = hashlib.sha256() 
        return digest

    # --- Atomic Methods (Parent Compliance) ---
    def calculate(self, payload: Union[str, bytes]) -> str:
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def validate(self, payload: Union[str, bytes], expected: str) -> bool:
        calculated = self.calculate(payload)
        return hmac.compare_digest(calculated, expected.lower())