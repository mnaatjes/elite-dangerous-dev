from abc import ABC, abstractmethod
from ..models import PersistenceProfile

class StrategyResolver(ABC):
    """
    Takes a target string and returns a complete Profile of Strategies
    """
    @abstractmethod
    def resolve(self, target: str) -> PersistenceProfile:
        pass