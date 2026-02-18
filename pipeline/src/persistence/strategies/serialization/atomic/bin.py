from typing import Any, Union
from ..abstract_atomic import SerializerStrategy

class AtomicBinarySerializer(SerializerStrategy):
    """
    Handles atomic encoding of data into binary format.
    
    In the context of the ETL pipeline, this is used for small binary 
    metadata or pre-transformed data blobs that fit entirely in memory.
    """

    def encode(self, data: Any) -> bytes:
        """
        Encodes data into bytes. 
        If data is already bytes, it passes through. 
        If it's a string, it encodes to utf-8.
        """
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode('utf-8')
        
        # If you need to support dicts here, you would use a protocol 
        # like pickle, but typically for your binary systems, 
        # the data arrives here already as 'bytes'.
        try:
            return bytes(data)
        except TypeError:
            raise ValueError(f"AtomicBinarySerializer cannot encode {type(data)}. "
                             "Data must be bytes-compatible.")

    def decode(self, payload: Union[str, bytes]) -> bytes:
        """
        Returns the raw binary payload. 
        Decouples the persistence layer from knowing the internal 
        binary structure of the star system records.
        """
        # Return bytes from bytes
        if isinstance(payload, bytes):
            return payload
        
        # Ensures encoded str into bytes
        if isinstance(payload, str):
            return payload.encode('utf-8')
        
        # Return Default
        return bytes(payload)