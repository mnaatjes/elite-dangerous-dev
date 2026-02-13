from pydantic_settings import BaseSettings
from pydantic import BaseModel, ConfigDict

class ETLNetworkSettings(BaseModel):
    # --- Prevent 'extra_forbidden' errors ---
    model_config = ConfigDict(extra='ignore')

    # --- Main Property Declarations ---
    user_agent: str = "Elite-Dangerous-ETL/1.0"
    pool_max_connections: int = 10
    default_retry_count: int = 3
    # Prioritize specific headers for integrity checks
    checksum_priority: list[str] = ["x-amz-meta-sha256", "x-goog-hash", "Digest", "ETag"]