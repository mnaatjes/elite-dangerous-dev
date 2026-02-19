# src/persistence/strategies/integrity/abstracts.py

from abc import ABC, abstractmethod
from typing import Union, Optional

from ..base import BaseStrategy

from abc import abstractmethod
from typing import Union
from ..base import BaseStrategy
from ..const import Capability, Category

class AbstractIntegrity(BaseStrategy):
    """Foundation for all Integrity checks."""
    CATEGORY = Category.INTEGRITY
    IS_ABSTRACT = True

class AtomicIntegrity(AbstractIntegrity):
    """For whole-payload validation (e.g., MD5 of a full file)."""
    CAPABILITIES = Capability.ATOMIC
    IS_ABSTRACT = True

    @abstractmethod
    def calculate(self, payload: Union[str, bytes]) -> str:
        pass

    @abstractmethod
    def validate(self, payload: Union[str, bytes], expected: str) -> bool:
        pass

class StreamingIntegrity(AbstractIntegrity):
    """For rolling hashes during ETL streams."""
    CAPABILITIES = Capability.STREAM
    IS_ABSTRACT = True

    @abstractmethod
    def update(self, chunk: Union[str, bytes]) -> None:
        """Updates internal hash state with new data."""
        pass

    @abstractmethod
    def finalize(self) -> str:
        """Returns final checksum."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Clears state for reuse."""
        pass