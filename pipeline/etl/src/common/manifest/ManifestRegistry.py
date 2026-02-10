from .BaseManifest import BaseManifest
from .schemas.DownloadRecordSchema import DownloadRecordSchema
from .schemas.ManifestSchema import ManifestSchema

class ManifestRegistry:
    # A mapping of domain to its specific Pydantic record schema
    _SCHEMA_MAP = {
        "systems": DownloadRecordSchema,
    }

    # The actual registry dict of manifest instances once created
    _instances = {}

    @classmethod
    def get_instance(cls, name:str) -> BaseManifest:
        pass

    @classmethod
    def list_all(cls):
        return list(cls._instances.keys())
    
    @classmethod
    def get_all(cls):
        return list(cls._instances.values())
    
    #@classmethod
    def __get_manifest(cls, root_dir, domain, process, version):
        # 1. Prepare data for validation
        config_data = {
            "root_dir": root_dir,
            "domain": domain,
            "process": process,
            "etl_version": version,
            "record_schema": cls._SCHEMA_MAP.get(domain)
        }

        # 2. VALIDATE: Registry uses the ManifestSchema here
        # This catches errors before BaseManifest even exists
        valid_config = ManifestSchema(**config_data)

        # 3. CONSTRUCT: Pass validated data to the class
        """return DownloadManifest(
            root_dir=valid_config.root_dir,
            domain=valid_config.domain,
            process=valid_config.process,
            etl_version=valid_config.etl_version,
            schema=valid_config.record_schema
        )
        """