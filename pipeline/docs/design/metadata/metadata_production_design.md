# Metadata Production Design: A Unified Approach

This document outlines a robust strategy for metadata production across the entire ELT pipeline, emphasizing the creation of a metadata JSON file for every significant interaction, download, or production of a derivative source-file. This approach is fundamental to establishing a strong "Chain of Custody" and ensuring data lineage, traceability, reproducibility, and effective debugging.

## 1. The Imperative for Pervasive Metadata

In a complex ELT pipeline managing large datasets like Elite Dangerous, metadata is not merely supplementary information; it is essential for:

-   **Traceability:** The ability to pick up any file (raw download, sample, processed data) and trace its complete journey back to its original source, including URL, download time, and all transformations applied.
-   **Reproducibility:** Documenting the exact conditions under which a file was generated or modified, including code versions, parameters, and input hashes, is crucial for recreating results.
-   **Debugging & Validation:** Metadata provides immediate context for problematic files. Is the schema different? Was the download incomplete? Metadata answers these questions, preventing costly re-processing.
-   **Pipeline State Management:** Metadata allows the pipeline to make intelligent decisions (e.g., has this version of the file already been processed?), avoiding redundant work and ensuring idempotency.

## 2. Metadata Models: Defining the Data Contract

Just as with our sampler, each stage of the pipeline that produces or significantly alters a file should have its own dedicated Pydantic model for its associated metadata. These models act as data contracts, ensuring consistency and validation.

```python
# common/models/metadata.py
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Re-using from Sampler Module for consistency
class CompressionType(str, Enum):
    GZIP = "gzip"
    BZIP2 = "bz2"
    NONE = "none"

class DownloadMetadata(BaseModel):
    """Metadata for a raw downloaded file."""
    source_url: str
    download_timestamp: datetime = Field(default_factory=datetime.utcnow)
    etag: Optional[str] = None
    sha256: str = Field(..., description="SHA256 hash of the downloaded file content.")
    compressed_size: int = Field(..., description="Size of the file on disk in bytes.")
    uncompressed_size_estimate: Optional[int] = Field(None, ge=0, description="Estimated size after decompression.")
    compression: CompressionType
    
    # Optional: could add downloader_version, retry_attempts, etc.

class SampleMetadata(BaseModel):
    """Metadata for a generated sample file."""
    parent_sha256: str = Field(..., description="SHA256 hash of the original raw download.")
    sample_sha256: str = Field(..., description="SHA256 hash of the sample file content.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    regime_type: str = Field(..., description="Type of sampling performed (e.g., 'head', 'random', 'systematic').")
    n_rows: int = Field(..., description="Number of records captured in the sample.")
    source_offset: Optional[int] = Field(None, description="Starting position in the source file.")
    strategy_used: str = Field(..., description="Name of the sampling strategy class used.")
    sampler_version: str = Field("1.0", description="Version of the sampler logic.")

class ProcessedMetadata(BaseModel):
    """Metadata for a file after a processing/transformation step."""
    parent_sha256: str = Field(..., description="SHA256 hash of the input file to this process (could be raw, sample, or another processed file).")
    processed_sha256: str = Field(..., description="SHA256 hash of the output processed file content.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transformation_name: str = Field(..., description="Name of the transformation applied (e.g., 'SchemaEnrichment', 'FieldNormalization').")
    transformation_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for the transformation.")
    processor_version: str = Field("1.0", description="Version of the processing logic.")
    # Add fields for schema_version, dependencies, etc.
```

## 3. The `MetadataFactory`: A Centralized Creation Point

To ensure consistency and simplify metadata generation, a `MetadataFactory` class will be introduced. This factory will be responsible for encapsulating the logic of *how* to construct each type of metadata object. It will calculate hashes, extract relevant information, and populate the Pydantic models.

```python
# common/metadata_factory.py
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Type, TypeVar, Any

# Assuming all models (DownloadMetadata, SampleMetadata, ProcessedMetadata, etc.) are imported
from .models.metadata import DownloadMetadata, SampleMetadata, ProcessedMetadata, CompressionType, FileMetadata

T = TypeVar('T', bound=BaseModel)

class MetadataFactory:
    """
    Centralized factory for creating various metadata objects.
    Ensures consistent hash calculation and model population.
    """

    def _calculate_sha256(self, file_path: Path) -> str:
        """Helper to calculate SHA256 of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_file_size(self, file_path: Path) -> int:
        """Helper to get file size."""
        return file_path.stat().st_size

    def create_download_metadata(
        self,
        source_url: str,
        download_path: Path,
        response_headers: Dict[str, str],
        compression_type: CompressionType,
        uncompressed_size_estimate: Optional[int] = None
    ) -> DownloadMetadata:
        """Creates metadata for a raw downloaded file."""
        file_sha256 = self._calculate_sha256(download_path)
        compressed_size = self._get_file_size(download_path)
        etag = response_headers.get('ETag') or response_headers.get('etag')

        return DownloadMetadata(
            source_url=source_url,
            download_timestamp=datetime.utcnow(),
            etag=etag,
            sha256=file_sha256,
            compressed_size=compressed_size,
            uncompressed_size_estimate=uncompressed_size_estimate,
            compression=compression_type
        )

    def create_sample_metadata(
        self,
        parent_meta: FileMetadata, # Using FileMetadata for parent context
        sample_path: Path,
        regime_type: str,
        n_rows: int,
        strategy_used: str,
        source_offset: Optional[int] = None,
        sampler_version: str = "1.0"
    ) -> SampleMetadata:
        """Creates metadata for a generated sample file."""
        sample_sha256 = self._calculate_sha256(sample_path)
        
        return SampleMetadata(
            parent_sha256=parent_meta.sha256,
            sample_sha256=sample_sha256,
            created_at=datetime.utcnow(),
            regime_type=regime_type,
            n_rows=n_rows,
            source_offset=source_offset,
            strategy_used=strategy_used,
            sampler_version=sampler_version
        )
    
    def create_processed_metadata(
        self,
        parent_sha256: str,
        processed_file_path: Path,
        transformation_name: str,
        transformation_params: Optional[Dict[str, Any]] = None,
        processor_version: str = "1.0"
    ) -> ProcessedMetadata:
        """Creates metadata for a file after a processing/transformation step."""
        processed_sha256 = self._calculate_sha256(processed_file_path)

        return ProcessedMetadata(
            parent_sha256=parent_sha256,
            processed_sha256=processed_sha256,
            created_at=datetime.utcnow(),
            transformation_name=transformation_name,
            transformation_params=transformation_params or {},
            processor_version=processor_version
        )
```

## 4. Integration into the Pipeline

The `MetadataFactory` will be injected as a dependency into the components responsible for creating or saving files (e.g., the `ArtifactManager` of the Sampler module, or a `Downloader` class).

### Example: Integrating with Sampler's `ArtifactManager`

The `ArtifactManager` will delegate the actual creation of the `SampleMetadata` object to the `MetadataFactory`.

```python
# src/sampler/artifact.py (Modified)
import json
from pathlib import Path
# Assuming MetadataFactory is imported
from common.metadata_factory import MetadataFactory
from .models import FileMetadata, SampleMetadata, SampleArtifact

class ArtifactManager:
    def __init__(
        self,
        metadata_factory: MetadataFactory, # Inject the MetadataFactory
        base_dir: Path = Path("etl/data/samples")
    ):
        self.metadata_factory = metadata_factory
        self.base_dir = base_dir

    def save_sample(
        self,
        data: list,
        parent_meta: FileMetadata,
        n_rows: int,
        strategy_used: str, # Changed from strategy_name for consistency with SampleMetadata
        regime_type: str = "head", # Added for SampleMetadata
        source_offset: Optional[int] = None # Added for SampleMetadata
    ) -> SampleArtifact:
        # ... (rest of the file saving logic) ...

        # Delegate metadata creation to the injected factory
        metadata = self.metadata_factory.create_sample_metadata(
            parent_meta=parent_meta,
            sample_path=sample_file_path,
            regime_type=regime_type,
            n_rows=n_rows,
            strategy_used=strategy_used,
            source_offset=source_offset
            # sampler_version could be passed here if dynamic
        )
        
        meta_file_path.write_text(metadata.model_dump_json(indent=2))
        
        return SampleArtifact(
            sample_path=sample_file_path,
            meta_path=meta_file_path,
            metadata=metadata
        )
```

### Example: Integrating with a `Downloader` (New Component)

A `Downloader` class would also be injected with the `MetadataFactory` to produce its `DownloadMetadata`.

```python
# src/downloader/downloader.py (Illustrative Example)
import requests
from pathlib import Path
from common.metadata_factory import MetadataFactory
from common.models.metadata import DownloadMetadata, CompressionType

class Downloader:
    def __init__(
        self,
        metadata_factory: MetadataFactory,
        target_dir: Path = Path("etl/data/downloads")
    ):
        self.metadata_factory = metadata_factory
        self.target_dir = target_dir

    def download_file(self, url: str) -> DownloadMetadata:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Determine path and compression type (simplified)
        # Assuming a utility for generating timestamped paths and filenames
        # Example: download_path = self.target_dir / "2026/03/my_file.json.gz"
        download_path = Path("placeholder/path/to/download.json.gz") # Replace with actual logic
        compression_type = CompressionType.GZIP # Replace with actual logic

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        download_meta = self.metadata_factory.create_download_metadata(
            source_url=url,
            download_path=download_path,
            response_headers=dict(response.headers),
            compression_type=compression_type
        )
        
        # Save the metadata alongside the downloaded file
        meta_path = download_path.parent / f"meta_{download_path.name.replace('.json.gz', '.json')}"
        meta_path.write_text(download_meta.model_dump_json(indent=2))

        return download_meta
```

This unified metadata production strategy ensures that metadata is consistently generated and managed across the entire pipeline, reinforcing the "Chain of Custody" at every step.