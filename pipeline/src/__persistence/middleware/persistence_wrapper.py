from typing import Iterable, Any
from ..strategies.serialization import StreamingSerializer
from ..strategies.integrity import StreamingIntegrity

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
            if isinstance(serializer, StreamingSerializer):
                chunk = serializer.encode_item(chunk)
            
            # 2. Type Guard: Ensure chunk is bytes for Integrity and Adapter
            # This satisfies VSCode/Pylance and prevents runtime Hash errors
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')
            
            # 3. Integrity Observation
            if isinstance(integrity, StreamingIntegrity):
                # VSCode is happy now because chunk is guaranteed to be bytes
                integrity.update(chunk)
            
            yield chunk