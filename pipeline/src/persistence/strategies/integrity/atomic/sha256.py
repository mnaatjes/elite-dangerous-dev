# --- Libraries ---
import hashlib
from typing import Union
from hmac import compare_digest

# --- Dependencies ---
from ..abstract_atomic import IntegrityStrategy

class AtomicSha256Strategy(IntegrityStrategy):
    """
    Concrete implementation of IntegrityStrategy using the SHA-256 algorithm.
    """

    def calculate(self, payload: Union[str, bytes]) -> str:
        """
        Calculates the SHA-256 hash of the given payload.
        """
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        
        return hashlib.sha256(payload).hexdigest()

    def validate(self, payload: Union[str, bytes], expected: str) -> bool:
        """
        Validates the payload by comparing its calculated hash with the expected value.
        Uses compare_digest to prevent timing attacks.
        """
        calculated = self.calculate(payload)
        return compare_digest(calculated, expected.lower())