from abc import ABC, abstractmethod
from ..models import PersistenceProfile

class AbstractStrategyResolver(ABC):
    @abstractmethod
    def resolve(self, target: str) -> PersistenceProfile:
        pass