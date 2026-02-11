from pydantic import BaseModel
from .metadata_schema import ManifestMetadataSchema

class ManifestSchema(BaseModel):
    metadata: 