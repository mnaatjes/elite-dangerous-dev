from .repository import ManifestRepository
from ..metadata import Metadata
from .models import Record

class ManifestService:
    def __init__(self, repository:ManifestRepository) -> None:
        self._repo = repository

    def add_entry(self, record:Record) -> None:
        pass

    def register_artifact(self, metadata:Metadata) -> None:
        pass