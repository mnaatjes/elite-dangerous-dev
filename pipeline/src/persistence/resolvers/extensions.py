import os
from ..interfaces.strategies import AbstractStrategyResolver
from ..interfaces.models import PersistenceProfile

class ExtensionStrategyResolver(AbstractStrategyResolver):
    def __init__(self, profiles: dict[str, PersistenceProfile], default: PersistenceProfile):
        self._profiles = profiles
        self._default = default

    def resolve(self, target: str) -> PersistenceProfile:
        _, ext = os.path.splitext(target.lower())
        return self._profiles.get(ext, self._default)