from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, DirectoryPath

# --- Metadata Schema for JSON files ---
class ManifestManagerSchema(BaseModel):
    """
    Schema for a single pipeline execution record.
    """
    # Allow arbitrary types if you use custom objects, 
    # - For my class definitions
    # - Formats datetime objects
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )
    # Properties of Schema
    root_dir: DirectoryPath = Field(
        ..., 
        description="The base directory on the Linux filesystem where JSON files are stored."
    )
    etl_version: str = Field(
        ..., 
        pattern=r"^\d+\.\d+$", 
        description="Version of the ETL Pipeline used to create manifest"
    )