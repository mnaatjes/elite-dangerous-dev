from abc import abstractmethod
from .abstract_atomic import IntegrityStrategy

class StreamingIntegrityStrategy(IntegrityStrategy):
    """Extended interface for chunk-based processing."""
    @abstractmethod
    def update(self, chunk: bytes) -> None:
        pass

    @abstractmethod
    def finalize(self) -> str:
        pass