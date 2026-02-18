from abc import ABC, abstractmethod
from typing import Union

class StreamingSerializerStrategy(ABC):
    """
    Purpose: To handle infrastructure-level encoding (compression, framing, 
    or header injection) for data streams in a memory-efficient manner.

    Do's and Don'ts:
    - SHOULD focus on storage-level representation (e.g., Gzip, Magic Numbers).
    - SHOULD NOT contain business logic or domain-specific data conversion.
    - SHOULD maintain internal state (buffers) across chunks if required.
    """

    @abstractmethod
    def encode_chunk(self, chunk: Union[str, bytes]) -> Union[str, bytes]:
        """
        Encodes a single chunk of data for the persistence medium.
        
        Example: If using compression, this returns a compressed block.
        If the encoder requires a minimum block size, it may return an 
        empty value while buffering the input.
        """
        pass

    @abstractmethod
    def flush(self) -> Union[str, bytes]:
        """
        Finalizes the encoding process and returns any remaining buffered bytes.
        
        This is critical for closing envelopes (footers) or pushing the 
        final bits of a compression dictionary to the disk.
        """
        pass