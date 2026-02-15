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

## 3.3. `SampleMetadata` (Output)

This is the metadata file (`sample.meta.json`) that is saved alongside the `sample.json`. It provides the complete "Chain of Custody" and context for the generated sample artifact.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SampleMetadata(BaseModel):
    """The final metadata artifact for a generated sample."""
    # Lineage and Integrity
    parent_sha256: str = Field(..., description="The SHA256 hash of the parent raw file, linking it to the source.")
    sample_sha256: str = Field(..., description="The SHA256 hash of the sample file itself, ensuring its integrity.")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Sampling Regime Details (How the sample was taken)
    regime_type: str = Field(..., description="The type of sampling performed, e.g., 'head', 'random', 'systematic'.")
    n_rows: int = Field(..., description="The number of records captured in the sample.")
    source_offset: Optional[int] = Field(None, description="The starting position (byte or line offset) within the source file.")
    
    # Execution Context (What created the sample)
    strategy_used: str = Field(..., description="The name of the strategy class used, e.g., 'GzipIJsonStrategy'.")
    sampler_version: str = Field("1.0", description="Version of the sampler logic to track changes over time.")
```

## 3.4. `SampleOutput` (Return Value)

This model represents the final return value of the `SamplerManager.run()` method. It provides a clean, structured object containing the paths to the generated artifacts and their metadata.

```python
from pydantic import BaseModel, FilePath

class SampleOutput(BaseModel):
    """The final output of a successful sampling operation."""
    sample_path: FilePath
    metadata_path: FilePath
    metadata: SampleMetadata
```