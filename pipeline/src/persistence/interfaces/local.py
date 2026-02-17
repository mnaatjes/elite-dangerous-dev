from pathlib import Path
from .abstract import PersistenceFactory

class LocalPersistenceFactory(PersistenceFactory):

    def __init__(self, root: str | Path, adapter) -> None:
        super().__init__(root)

        # Set dependencies
        self._adapter = adapter

        # Map strategies to instances
        self._serializers = {
            ".json": "JsonSerializer()"
        }