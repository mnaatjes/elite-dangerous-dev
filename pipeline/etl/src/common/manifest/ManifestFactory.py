import BaseManifest

class ManifestFactory:
    _registry = {
        #"downloads": (DownloadManifest, "etl/manifests/downloads.json"),
        #"processed": (ProcessedManifest, "etl/manifests/processed.json")
    }

    @classmethod
    def get_manifest(cls, manifest_type: str) -> BaseManifest:
        if manifest_type not in cls._registry:
            raise ValueError(f"Unknown manifest type: {manifest_type}")
        
        klass, default_path = cls._registry[manifest_type]
        return klass(default_path)