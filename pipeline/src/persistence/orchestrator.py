# --- Libraries ---
from typing import Any, Iterable

# --- Dependencies ---
from .middleware import PersistenceStreamProcessor
from .strategies import StreamingSerializerStrategy

class PersistenceOrchestrator:
    """
    Product of the Persistence Factory. The Fascade for services and dependencies
    given a specific implementation (local, db, cloud, etc)
    - NOT the entry point
    - Should NOT know infrastructure logic
    - Holds dependencies
    - Product of Persistent Factory
    - User-Access Layer (Repositories) receive Orchestrator
    - Meso Component
    - Required Categories of Dependencies
        1. Infrastructure - Adapter (Where)
        2. Transformation - Serializer (What)
        3. Integrity - Validation and Safety (Proof)
    """
    def __init__(self, adapter, profile) -> None:
        self._adapter    = adapter
        self._serializer = profile.serializer
        self._integrity  = profile.integrity
    
    def save_atomic(self, target: str, data: Any) -> str:
        """
        Handles small payloads by encoding and hashing the entire object in memory.
        :return: Checksum string (Source of Truth).
        """
        # 1. Infrastructure Encoding (e.g., dict -> json string)
        # Using 'encode' as per our AtomicSerializerStrategy abstract
        payload = self._serializer.encode(data)
        
        # 2. Integrity Calculation
        checksum = self._integrity.calculate(payload)

        # 3. Persistence via Adapter
        self._adapter.write(target, payload)

        return checksum

    def save_stream(self, target: str, data_generator: Iterable, mode: str = "wb") -> str:
        """
        Orchestrates a memory-efficient streaming write.
        
        The middleware handles the heavy lifting of ensuring data is 
        encoded and hashed in the correct order before being passed to 
        the adapter for physical I/O.

        Selection is an Intent Signal that the data cannot fit in the RAM and
        therefore MUST be streamed
        - This bypasses any Atomic Serializers; as data already chunked
        """
        # 1. Wrap the raw generator with our Encoding + Integrity middleware
        # This transforms the source into a finalized byte-stream
        processed_stream = PersistenceStreamProcessor.wrap(
            source=data_generator,
            serializer=self._serializer,
            integrity=self._integrity
        )

        # 2. Hand off the processed generator to the Adapter (the Sink)
        # The adapter is now guaranteed to receive a stream of 'bytes'
        self._adapter.write_stream(
            target=target,
            data_generator=processed_stream,
            mode=mode
        )

        # 3. Finalize the integrity fingerprint and return it
        return self._integrity.finalize()