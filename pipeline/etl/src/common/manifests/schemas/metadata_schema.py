from pathlib import Path
from datetime import datetime, timezone
from typing import Dict
from pydantic import BaseModel, Field, ConfigDict, DirectoryPath
from ...constants import ETLProcess, ETLDomain
from .record_schema import ManifestRecordSchema

# --- Metadata Schema for JSON files ---
class ManifestMetadataSchema(BaseModel):
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
    process: ETLProcess = Field(
        ..., 
        description="From Enum in constants.py | Process that specific manifest performs"
    )
    ts_executed: datetime | None = Field(
        default=None,
        description="Datetime obj when the last process was executed"
    )
    ts_created: datetime | None = Field(
        default=None,
        description="Datetime obj when the manifest was created"
    )
    ts_updated: datetime | None = Field(
        default=None,
        description="Datetime obj from the last update of the manifest document"
    )
    total_records: int = Field(
        ge=0, 
        description="The total number of records processed"
    )
    records: Dict[str, ManifestRecordSchema] = Field(
        default_factory=dict,
        description="A record representing an individual file from the ETL process"
    )