
from pathlib import Path
from .metadata import Metadata as ManifestMeta
from .record import Record as ManifestRecord
from ..common.path_manager import PathManager
from ..config.model import ETLConfig
from ..manifest.model import Manifest
from ..extractor.download.event import DownloadEvent
from ..extractor.sources.model import ETLSource

class ManifestManager:
    def __init__(self, path_manager:PathManager, config:ETLConfig) -> None:
        self.pm     = path_manager
        self.conf   = config

    # --- Helper Methods ---

    def _generate_new_manifest(self, process_name:str, version:str) -> Manifest:
        """
        Creates a fresh Manifest skeleton in memory. 
        Follows the Design Pattern: No I/O in constructors or initialization.
        """
        # 1. Prepare Metadata following your refactored schema
        metadata = ManifestMeta(
            process=process_name,
            version=version
        )

        # 2. Return the Manifest Data Object
        # 'records' is automatically initialized as {} via default_factory
        return Manifest(
            process=process_name,
            metadata=metadata
        )
    
    # --- Property Modifications ---
    def add_record(self, manifest: Manifest, source: ETLSource, event: DownloadEvent) -> None:
        """
        Converts a DownloadEvent into a ManifestRecord and updates the Manifest.
        """
        # 1. Create the immutable Record object
        record = ManifestRecord(
            source_id=source.source_id,
            dataset=source.dataset,
            checksum=event.sha256,
            file_path=event.file_path,
            file_size=event.file_size_bytes,
            etag=source.state.last_etag,
            ts_downloaded=event.ts_download_completed,
            file_version="1.0"
        )

        # 2. Add to the manifest dictionary (keyed by SHA256)
        manifest.records[record.checksum] = record
        
        # 3. Synchronize metadata
        manifest.metadata.total_records = len(manifest.records)
        manifest.metadata.touch()

        # 4. Persistence (Explicit is Better than Implicit)
        self.save(manifest)

    # --- File I/O Methods ---

    def load(self, process_name:str, version:str) -> Manifest:
        path = self.pm.generate_manifest_path(
            process=process_name,
            version=version
        )

        # Load manifest object and sub-models (metadata, records)
        manifest = self.pm.read_pydantic_model(
            path=path,
            model_class=Manifest,
            strict=False
        )

        # Check if none
        if manifest is None:
            return self._generate_new_manifest(
                process_name=process_name,
                version=version
            )
        
        # Return default
        return manifest
    
    def save(self, manifest: Manifest) -> None:
        """
        Persists the Manifest to the filesystem.
        Delegates I/O and atomicity logic to the PathManager.
        """
        # 1. Update metadata timestamps and record counts before saving
        manifest.metadata.touch()
        manifest.metadata.total_records = len(manifest.records)

        # 2. Resolve the destination path using the PathManager
        # We use the manifest's own metadata to find the correct filename
        target_path = self.pm.generate_manifest_path(
            process=manifest.process,
            version=manifest.metadata.version
        )

        # 3. Execute the write via PathManager
        # This uses your established 'atomic' logic and Pydantic serialization
        self.pm.write_pydantic_model(
            path=target_path,
            model=manifest,
            atomic=True
        )