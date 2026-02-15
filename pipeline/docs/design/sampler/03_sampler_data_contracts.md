# 3. Sampler Module: Data Contracts (Pydantic Models)

This document serves as a single source of truth for the data structures and contracts used throughout the Sampler module. Using Pydantic models ensures that data is validated and that the shape of the data is explicit and consistent between components.

## 3.1. `FileMetadata` (Input)

This model represents the initial, high-level metadata provided by an external component like the `PathManager`. It contains basic information about the file on the filesystem.

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, FilePath

class CompressionType(str, Enum):
    GZIP = "gzip"
    BZIP2 = "bz2"
    NONE = "none"

class FileMetadata(BaseModel):
    """Basic filesystem and source metadata for a downloaded file."""
    file_path: FilePath
    source_url: Optional[str] = None
    etag: Optional[str] = None
    sha256: str # Added to link parent to child
    
    # Sizes
    compressed_size: int = Field(..., description="Size in bytes on disk.")
    uncompressed_size_estimate: int = Field(..., ge=0, description="Estimated size after decompression.")
    
    # Assumed properties (can be confirmed by Sniffer)
    compression: CompressionType
    
    # Timing
    downloaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = True # Data is read-only
```

## 3.2. `SnifferResult` (Internal)

This model represents the output of the `Sniffer`. It contains the "ground truth" about the file's internal structure and format, discovered by inspecting its contents.

```python
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class FileStructure(str, Enum):
    JSONL = "jsonl"           # Newline-delimited JSON objects
    JSON_ARRAY = "array"      # Standard JSON array, e.g., `[{}, {}]`
    JSON_OBJECT = "object"    # Standard JSON object, e.g., `{}`
    CSV = "csv"
    UNKNOWN = "unknown"       # Fallback for undetected or unsupported structures

class SnifferResult(BaseModel):
    """The 'Deep Inspection' record of the file's content."""
    model_config = ConfigDict(frozen=True)

    # Detected structural properties
    structure: FileStructure
    encoding: str = "utf-8"
    has_header: bool = False  # Relevant for CSV
    
    # Validation/Safety
    is_valid: bool = True
    corruption_note: Optional[str] = None
    
    # Discovery hints (e.g., first keys found in the JSON)
    schema_hint: List[str] = Field(default_factory=list)
```

## 3.3. `SampleMetadata` (Output Artifact)

This is the metadata model for the `sample.meta.json` sidecar file. It serves as the "birth certificate" for the generated sample, linking it back to its source and documenting how it was created.

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SampleMetadata(BaseModel):
    """The sidecar metadata for a created sample."""
    model_config = ConfigDict(frozen=True)

    parent_sha256: str = Field(..., description="SHA256 of the source download")
    sample_sha256: str = Field(..., description="SHA256 of this sample file")
    n_rows: int
    strategy_used: str
    created_at: datetime = Field(default_factory=datetime.now)
    regime: str = "head"  # e.g., head, tail, random
```

## 3.4. `SampleArtifact` (Return Value)

This model represents the final, cohesive package returned after a successful sampling run. It bundles together the paths to the created files and the rich metadata object.

```python
from pydantic import BaseModel
from pathlib import Path

class SampleArtifact(BaseModel):
    """The cohesive package returned after a successful sampling run."""
    sample_path: Path
    meta_path: Path
    metadata: SampleMetadata
```