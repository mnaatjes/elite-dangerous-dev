from typing import List

from src.persistence.orchestrator import PersistenceOrchestrator
from src.persistence.resolvers.abstract import StrategyResolver
from .abstract import PersistenceFactory
from ...adapters import AdapterFactory, Adapter

class LocalPersistenceFactory(PersistenceFactory):

    def __init__(self, adapter:Adapter, resolver:StrategyResolver) -> None:

        # Set dependencies
        self._adapter = adapter
        self._resolver = resolver

    @property
    def supported_formats(self) -> List[str]:
        # TODO: Get keys from resolver Profiles
        return [".json"]

    def get_orchestrator(self, target: str, **kwargs) -> PersistenceOrchestrator:
        # Deligate which toll to use to resolver
        profile = self._resolver.resolve(target)

        return PersistenceOrchestrator(
            adapter=self._adapter,
            profile=profile
        )