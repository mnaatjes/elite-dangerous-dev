from .repository import ManifestRepository
from ..metadata import Metadata
from .models import Record

class ManifestService:
    def __init__(self, repository:ManifestRepository) -> None:
        self._repo = repository

    # --- Read Methods ---
    def get_headers(self):
        pass

    def get_record(self, content_sha256):
        pass

    def list_by_status(self, status:str):
        # Returns list of processes based on 'status'
        # [PENDING, RUNNING, COMPLETED, FAILED, IN_PROGRESS, EXTRACTING]
        pass

    def get_last_run(self):
        # Return exact last process
        pass

    # --- Write Methods ---

    def add_entry(self, record:Record) -> None:
        pass

    def register_artifact(self, metadata:Metadata) -> None:
        pass

