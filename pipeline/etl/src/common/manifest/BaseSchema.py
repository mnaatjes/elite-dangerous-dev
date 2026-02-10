
from abc import ABC, abstractmethod
from typing import Dict, Any, Type

class BaseSchema(ABC):
    @abstractmethod
    def validate(self, data: Dict[str, Any]):
        pass