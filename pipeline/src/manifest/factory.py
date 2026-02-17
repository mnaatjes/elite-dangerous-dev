from .service import ManifestService
from .repository import ManifestRepository
from ..path_manager import PathManager

class ManifestServiceFactory:
    def __init__(self, path_manager:PathManager) -> None:
        self._pm = path_manager