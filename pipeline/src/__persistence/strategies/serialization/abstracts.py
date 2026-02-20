# src/persistence/strategies/serialization/abstracts.py

from abc import ABC, abstractmethod
from typing import Any, Union, Optional

from ..base import BaseStrategy
from ..const import Capability, Category

class AbstractSerializer(BaseStrategy):
    """Foundation for all Serializers."""
    CATEGORY = Category.SERIALIZER
    IS_ABSTRACT = True

class AtomicSerializer(AbstractSerializer):
    """Interface for whole-object encoding/decoding."""
    CAPABILITIES = Capability.ATOMIC
    IS_ABSTRACT = True

    @abstractmethod
    def encode(self, data: Any) -> Union[str, bytes]:
        pass

    @abstractmethod
    def decode(self, payload: Union[str, bytes]) -> Any:
        pass

class StreamingSerializer(AbstractSerializer):
    """Interface for item-by-item encoding (e.g., NDJSON)."""
    CAPABILITIES = Capability.STREAM
    IS_ABSTRACT = True

    @abstractmethod
    def encode_item(self, item: Any) -> Union[str, bytes]:
        """Encodes a single 'row' or object for a stream."""
        pass

    @abstractmethod
    def finalize(self) -> Union[str, bytes]:
        """Returns any closing bytes (footers, closing brackets)."""
        pass