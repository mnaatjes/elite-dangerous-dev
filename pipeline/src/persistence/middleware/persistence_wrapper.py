from typing import Iterable, Any
from ..strategies.serialization import StreamingSerializerStrategy
from ..strategies.integrity import StreamingIntegrityStrategy

class PersistenceStreamProcessor:
    """
    Middleware that bridges the gap between raw data sources and the Adapter.
    Coordinates the Encoding and Integrity cycles for streaming data.
    """
    @staticmethod
    def wrap(
        source: Iterable[Any], 
        serializer: Any, 
        integrity: Any
    ) -> Iterable[bytes]:
        
        for chunk in source:
            # 1. Infrastructure Encoding
            if isinstance(serializer, StreamingSerializerStrategy):
                chunk = serializer.encode_chunk(chunk)
            
            # 2. Type Guard: Ensure chunk is bytes for Integrity and Adapter
            # This satisfies VSCode/Pylance and prevents runtime Hash errors
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            
            # 3. Integrity Observation
            if isinstance(integrity, StreamingIntegrityStrategy):
                # VSCode is happy now because chunk is guaranteed to be bytes
                integrity.update(chunk)
            
            yield chunk