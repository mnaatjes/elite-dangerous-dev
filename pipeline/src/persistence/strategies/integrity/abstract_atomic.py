from abc import ABC, abstractmethod
from typing import Union

class IntegrityStrategy(ABC):
    @abstractmethod
    def calculate(self, payload:Union[str, bytes]) -> bool:
        pass

    @abstractmethod
    def validate(self, payload:Union[str, bytes], expected:str) -> bool:
        pass