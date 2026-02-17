from pathlib import Path

from src.persistence.orchestrator import PersistenceOrchestrator
from .abstract import PersistenceFactory
from ...filesystem.adapters import FilesystemAdapter

class LocalPersistenceFactory(PersistenceFactory):

    def __init__(self, adapter:FilesystemAdapter) -> None:

        # Set dependencies
        self._adapter = adapter

        # Map strategies to instances
        self._serializers = {
            ".json": "JsonSerializer()"
        }

    def supported_formats(self) -> list:
        return []

    def get_orchestrator(self, target: str, **kwargs) -> PersistenceOrchestrator:
        return PersistenceOrchestrator(
            adapter=self._adapter,
            serializer_strategy={},
            integrity_strategy={}
        )