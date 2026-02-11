from pydantic import BaseModel, Field

from ...constants import ETLDomain

class ManifestRecordSchema(BaseModel):
    domain: ETLDomain = Field(
        ...,
        description="The Elite Dangerous data domain which is the purview of the metadata"
    )