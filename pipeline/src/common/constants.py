from enum import Enum

# --- Naming Templates for PathManager / Naming Service
class NamingTemplate(str, Enum):
    METADATA="meta_{source}_{service}_{dataset}_{timestamp}_{version}.json"
    DOWNLOADS="{source}_{service}_{dataset}_{timestamp}_v{version}{extension}"
    MANIFEST="manifest_{service}_{version}.json"
    LOG="etl_{service}_{timestamp}.log"
    SAMPLE="sample_{source}_{service}_{dataset}_{timestamp}_v{version}{extension}"

# --- Compression Type for Metadata Service ---
class CompressionType(str, Enum):
    GZIP = "gzip"
    BZIP2 = "bz2"