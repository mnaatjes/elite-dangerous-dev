from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
from typing import Type, TypeVar, Literal, Union

# Define the generic for your record schemas
from pydantic import BaseModel as PydanticBaseModel
T = TypeVar("T", bound=PydanticBaseModel)

class ManifestSchema(BaseModel):
    """
    Validates the initialization parameters for a BaseManifest instance.
    Used by the ManifestRegistry to ensure proper construction.
    """
    # Allows the schema to handle complex types like 'Type' or 'Path'
    model_config = ConfigDict(arbitrary_types_allowed=True)

    root_dir: Union[Path, str] = Field(
        ..., 
        description="The base directory on the Linux filesystem where JSON files are stored."
    )
    
    # Restrict to specific ETL processes using Literal
    process: Literal["downloads", "processing", "ingestion", "validation"] = Field(
        ..., 
        description="The specific stage of the ETL pipeline."
    )
    
    # Restrict to specific data domains
    domain: Literal["stations", "systems", "bodies", "commodities"] = Field(
        ..., 
        description="The Elite Dangerous data domain."
    )
    
    etl_version: str = Field(
        default="1.0.0", 
        pattern=r"^\d+\.\d+$", # Enforces Semantic Versioning (e.g., 1.2.3)
        description="The version of the ETL logic creating this manifest."
    )
    
    # This expects the CLASS of the Pydantic model, not an instance
    record_schema: Type[T] = Field(
        ..., 
        description="The Pydantic model class used to validate individual records."
    )