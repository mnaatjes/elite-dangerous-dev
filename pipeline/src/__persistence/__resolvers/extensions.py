import os
from .abstract import StrategyResolver
from ..models import PersistenceProfile

class ExtensionStrategyResolver(StrategyResolver):
    def __init__(self, profiles: dict[str, PersistenceProfile], default: PersistenceProfile):
        self._profiles = profiles
        self._default = default

    def resolve(self, target: str) -> PersistenceProfile:
        _, ext = os.path.splitext(target.lower())
        return self._profiles.get(ext, self._default)