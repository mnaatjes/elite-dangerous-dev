
"""
Adapter Factory: main entry-point for all adapters / Infrastructure Layer
Serves as:
- Infrastructural Bootstrapper

"""

from typing import Dict
from .registry import FilesystemRegistry
from .filesystem import LocalFilesystemAdapter

class AdapterFactory:
    """
    Infrastructure Bootstrapper.
    Responsible for the assembly and wiring of I/O adapters.
    """

    @staticmethod
    def build_local_filesystem(settings) -> LocalFilesystemAdapter:
        """
        Assembles a fully-wired FilesystemAdapter using application settings.
        
        This method acts as the 'Master Electrician' for the infrastructure,
        connecting the Registry (The Map) to the Adapter (The Hand).
        """
        # 1. Extract the directory mapping from settings
        # This typically pulls properties like ETL_DIR__STAR_DATA from your .env
        directory_map: Dict[str, str] = settings.dir.model_dump()

        # 2. Instantiate the Infrastructure Map (Registry)
        # The Registry is the 'Phonebook' the adapter uses to find directories.
        registry = FilesystemRegistry(directory_map)

        # 3. Instantiate the Naming Policy
        # This ensures consistent file naming across the ETL pipeline.
        #naming_service = NamingService()

        # 4. Assemble the Adapter (The Implementation)
        # We inject the Registry and NamingService into the 'Local' implementation.
        # This keeps the Adapter 'dumb'—it only knows how to use the tools it's given.
        adapter = LocalFilesystemAdapter(
            filesystem_registry=registry
        )

        return adapter