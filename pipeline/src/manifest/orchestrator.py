from ..path_manager import PathManager
from .factory import ManifestServiceFactory

class ManifestOrchestrator:

    def __init__(self, settings, path_manager:PathManager) -> None:
        # Major Dependencies
        self._settings = settings
        self._pm = path_manager

        # Internal Factory
        self._factory = ManifestServiceFactory(self._pm)

        # Tracking instances and validation
        self._service_registry={}
        self._valid_services=["download", "sample"]

    def get_available_manifests(self) -> list:
        # Lists all available services
        return self._valid_services

    def list_created_services(self) -> list:
        return []
